"""Run against a newly initialized private local database, never historical data."""
import argparse
import os
from pathlib import Path
import sys
import tempfile
import unittest

parser=argparse.ArgumentParser()
parser.add_argument('--directory',required=True)
parser.add_argument('--service',required=True,choices=['erp-tur','turismo'])
args,remaining=parser.parse_known_args()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fresh_local import configure
configure(args.directory,args.service)
import django
django.setup()
from django.db import connection
from django.core.management import call_command
from django.test import Client
from schema_readiness import inspect_schema
from sqlite_snapshot import create_snapshot
call_command('check',fail_level='WARNING')


class FreshDatabaseChecks(unittest.TestCase):
    def test_01_full_schema_is_ready_over_http(self):
        self.assertEqual(inspect_schema(),{'status':'ready','checks':[]})
        response=Client(HTTP_HOST='localhost').get('/readyz')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json()['service'],args.service)

    def test_02_no_foreign_key_violations(self):
        with connection.cursor() as cursor:
            cursor.execute('PRAGMA foreign_key_check')
            self.assertEqual(cursor.fetchall(),[])

    def test_03_migrations_have_no_model_drift(self):
        call_command('makemigrations',check=True,dry_run=True,interactive=False,verbosity=0)

    def test_04_migrate_is_idempotent(self):
        with connection.cursor() as cursor:
            cursor.execute('SELECT COUNT(*) FROM django_migrations')
            before=cursor.fetchone()[0]
        call_command('migrate',interactive=False,verbosity=0)
        with connection.cursor() as cursor:
            cursor.execute('SELECT COUNT(*) FROM django_migrations')
            self.assertEqual(cursor.fetchone()[0],before)

    def test_05_private_backup_and_restore(self):
        source=Path(connection.settings_dict['NAME'])
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)/'snapshot.sqlite3'
            report=create_snapshot(source,target)
            self.assertTrue(report['restoration_verified'])
            self.assertGreater(report['tables'],100)
            self.assertEqual(target.stat().st_mode & 0o077,0)
            with self.assertRaises(FileExistsError):create_snapshot(source,target)

    def test_06_existing_directory_cannot_be_reinitialized(self):
        from fresh_local import initialize
        with self.assertRaises(FileExistsError):initialize(args.directory,args.service)

    def test_07_customer_http_round_trip_on_migrated_database(self):
        import uuid
        from django.db import transaction
        from api.models import CustomUser
        from apps.turismo.models import TourismProvider
        from rest_framework.test import APIClient
        # All synthetic business data is rolled back, including on assertion failure.
        with transaction.atomic():
            try:
                suffix=uuid.uuid4().hex
                owner=CustomUser(username='schema-owner-'+suffix,role='BUSINESS_OWNER')
                other=CustomUser(username='schema-other-'+suffix,role='BUSINESS_OWNER')
                CustomUser.objects.bulk_create([owner,other])
                TourismProvider.objects.create(owner=owner,name='Synthetic rollback-only',provider_type='GUIDE')
                TourismProvider.objects.create(owner=other,name='Synthetic rollback-only other',provider_type='GUIDE')
                route='/api/v1/mi-negocio/comercial/clientes/'
                client=APIClient(HTTP_HOST='localhost');client.force_authenticate(owner)
                response=client.post(route,{'nombre':'Rollback-only client','email':'rollback@example.test'},format='json')
                self.assertEqual(response.status_code,201,response.content)
                detail=route+str(response.json()['data']['id'])+'/'
                self.assertEqual(client.get(detail).status_code,200)
                self.assertEqual(client.patch(detail,{'telefono':'123'},format='json').status_code,200)
                client.force_authenticate(other)
                self.assertEqual(client.get(detail).status_code,404)
                self.assertEqual(client.patch(detail,{'nombre':'Injected'},format='json').status_code,404)
            finally:
                transaction.set_rollback(True)

    def test_08_wallet_two_approvals_http_and_replay(self):
        import uuid
        from decimal import Decimal
        from django.db import transaction
        from django.test import override_settings
        from api.models import CustomUser
        from apps.wallet.models import Wallet,WalletLimiteOperativo,WalletMovimiento
        from rest_framework.test import APIClient
        with transaction.atomic(),override_settings(WALLET_INTERNAL_TRANSFERS_ENABLED=True,WALLET_DEVICE_APPROVALS_REQUIRED=False):
            try:
                suffix=uuid.uuid4().hex
                owner=CustomUser(username='wallet-source-'+suffix,role='BUSINESS_OWNER')
                other=CustomUser(username='wallet-target-'+suffix,role='BUSINESS_OWNER')
                CustomUser.objects.bulk_create([owner,other])
                source=Wallet.objects.create(user_id=owner.pk,owner_type='CORPORATIVO',owner_id=suffix+'a',currency='COP',saldo_disponible='100')
                destination=Wallet.objects.create(user_id=other.pk,owner_type='CORPORATIVO',owner_id=suffix+'b',currency='COP')
                WalletLimiteOperativo.objects.create(wallet=source,monto_maximo_transaccion='20',monto_maximo_diario='40')
                client=APIClient(HTTP_HOST='localhost');client.force_authenticate(owner)
                route='/api/v1/finance/wallet/transfers/'
                response=client.post(route,{'source':str(source.pk),'destination':str(destination.pk),'amount':'10.00','idempotency_key':str(uuid.uuid4())},format='json')
                self.assertEqual(response.status_code,201,response.content)
                intent=response.json()['data'];detail=route+intent['id']+'/'
                first=client.post(detail+'review/',{'digest':intent['digest']},format='json')
                self.assertEqual(first.status_code,200,first.content)
                source.refresh_from_db();self.assertEqual(source.saldo_disponible,Decimal('100'))
                confirmation={'digest':intent['digest'],'confirmation':first.json()['data']['confirmation']}
                second=client.post(detail+'execute/',confirmation,format='json');self.assertEqual(second.status_code,200,second.content)
                repeated=client.post(detail+'execute/',confirmation,format='json');self.assertEqual(repeated.status_code,200,repeated.content)
                self.assertEqual(second.json()['data']['transaction'],repeated.json()['data']['transaction'])
                source.refresh_from_db();destination.refresh_from_db()
                self.assertEqual((source.saldo_disponible,destination.saldo_disponible),(Decimal('90'),Decimal('10')))
                self.assertEqual(WalletMovimiento.objects.filter(transaccion_id=second.json()['data']['transaction']).count(),2)
            finally:
                transaction.set_rollback(True)

    def test_09_device_signed_approvals_on_migrated_database(self):
        import base64,uuid
        from django.db import transaction
        from django.test import override_settings
        from django.utils import timezone
        from datetime import timedelta
        from api.models import CustomUser
        from apps.wallet.models import Wallet,WalletDeviceCredential,WalletLimiteOperativo
        from apps.wallet.services import device_approvals,internal_transfer
        from cryptography.hazmat.primitives import hashes,serialization
        from cryptography.hazmat.primitives.asymmetric import ec
        class ProtocolFixtureVerifier:
            def check_registered(self,credential):pass  # Isolated fixture, not attestation.
        audience=uuid.uuid4()
        with transaction.atomic(),override_settings(WALLET_INTERNAL_TRANSFERS_ENABLED=True,WALLET_DEVICE_APPROVALS_REQUIRED=True,WALLET_APPROVAL_AUDIENCE=str(audience),WALLET_ATTESTATION_VERIFIER=ProtocolFixtureVerifier()):
            try:
                owner=CustomUser(username='device-rollback-'+uuid.uuid4().hex,role='BUSINESS_OWNER')
                recipient=CustomUser(username='device-recipient-'+uuid.uuid4().hex,role='BUSINESS_OWNER')
                CustomUser.objects.bulk_create([owner,recipient])
                source=Wallet.objects.create(user_id=owner.pk,owner_type='CORPORATIVO',owner_id=str(uuid.uuid4()),currency='COP',saldo_disponible='100')
                target=Wallet.objects.create(user_id=recipient.pk,owner_type='CORPORATIVO',owner_id=str(uuid.uuid4()),currency='COP')
                WalletLimiteOperativo.objects.create(wallet=source,monto_maximo_transaccion='20',monto_maximo_diario='40')
                key=ec.generate_private_key(ec.SECP256R1())
                public=base64.b64encode(key.public_key().public_bytes(serialization.Encoding.X962,serialization.PublicFormat.UncompressedPoint)).decode()
                # Synthetic preverified record tests the protocol, not vendor attestation.
                device=WalletDeviceCredential.objects.create(user_id=owner.pk,audience=audience,public_key=public,status='VERIFIED',enrollment_nonce_hash='0'*64,enrollment_expires_at=timezone.now()+timedelta(minutes=5),valid_until=timezone.now()+timedelta(days=1))
                intent=internal_transfer.prepare(owner,source.pk,target.pk,'10',uuid.uuid4())
                def signed(phase):
                    challenge,message=device_approvals.issue(owner,intent.pk,device.pk,phase)
                    return {'challenge':challenge.pk,'signature':base64.b64encode(key.sign(message,ec.ECDSA(hashes.SHA256()))).decode()}
                intent,token=internal_transfer.review(owner,intent.pk,intent.digest,signed('REVIEW'))
                result=internal_transfer.execute(owner,intent.pk,intent.digest,token,signed('EXECUTE'))
                self.assertEqual(result.state,'EXECUTED')
                source.refresh_from_db();target.refresh_from_db()
                self.assertEqual((str(source.saldo_disponible),str(target.saldo_disponible)),('90.00','10.00'))
            finally:
                transaction.set_rollback(True)


if __name__=='__main__':unittest.main(argv=[sys.argv[0],*remaining])
