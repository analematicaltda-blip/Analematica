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


if __name__=='__main__':unittest.main(argv=[sys.argv[0],*remaining])
