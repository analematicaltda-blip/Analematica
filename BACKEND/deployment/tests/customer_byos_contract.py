"""Separate PostgreSQL customer fixture, actual AEAD bytes and restricted writer."""
import base64,json,os,uuid
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

def run_customer_contract(source,role,password,company_id,database):
    from django.db import DatabaseError
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.keywrap import aes_key_wrap,aes_key_unwrap
    from apps.core_erp.accounting.customer_postgres_store import CustomerPostgresStore,StorageConflict,initialize_customer_store
    owner=source.copy(alias='customer_owner_probe');owner.settings_dict['NAME']=database
    writer=None;quoted_role=source.ops.quote_name(role)
    company=str(company_id);document=str(uuid.uuid4());kek=os.urandom(32);dek=os.urandom(32);iv=os.urandom(12)
    encode=lambda b:base64.urlsafe_b64encode(b).rstrip(b'=').decode()
    aad=json.dumps(['sgacd-fiscal-envelope-v1','AES-256-GCM+A256KW',company,document,'fiscal-document'],separators=(',',':')).encode()
    plaintext=b'Synthetic customer-owned fiscal document'
    envelope={'schema':'sgacd-fiscal-envelope-v1','algorithm':'AES-256-GCM+A256KW','context':{'company_id':company,'document_id':document},
              'iv':encode(iv),'wrapped_key':encode(aes_key_wrap(kek,dek)),'ciphertext':encode(AESGCM(dek).encrypt(iv,plaintext,aad))}
    try:
        try:initialize_customer_store(source,company)
        except ValueError:pass
        else:raise AssertionError('Provider ledger must not be accepted as BYOS destination.')
        initialize_customer_store(owner,company)
        with owner.cursor() as cursor:
            cursor.execute('GRANT USAGE ON SCHEMA public TO '+quoted_role)
            cursor.execute('GRANT SELECT ON public.customer_fiscal_binding TO '+quoted_role)
            cursor.execute('GRANT SELECT,INSERT ON public.customer_fiscal_envelopes TO '+quoted_role)
        writer=owner.copy(alias='customer_writer_probe');writer.settings_dict.update(USER=role,PASSWORD=password)
        store=CustomerPostgresStore(writer,company);receipt=store.put(envelope)
        assert receipt['stored'] and not receipt['replayed'];assert store.put(envelope)['replayed']
        restored=store.get(document);assert restored==envelope
        raw_key=aes_key_unwrap(kek,base64.urlsafe_b64decode(restored['wrapped_key']+'='*((-len(restored['wrapped_key']))%4)))
        ciphertext=base64.urlsafe_b64decode(restored['ciphertext']+'='*((-len(restored['ciphertext']))%4))
        assert AESGCM(raw_key).decrypt(iv,ciphertext,aad)==plaintext
        new_iv=os.urandom(12)
        changed={**envelope,'iv':encode(new_iv),'ciphertext':encode(AESGCM(dek).encrypt(new_iv,b'Different synthetic bytes',aad))}
        try:store.put(changed)
        except StorageConflict:pass
        else:raise AssertionError('Existing document version must not be overwritten.')
        assert store.get(document)==envelope
        try:CustomerPostgresStore(writer,uuid.uuid4())
        except ValueError:pass
        else:raise AssertionError('A different company must not use this binding.')
        try:
            with writer.cursor() as cursor:cursor.execute('DELETE FROM public.customer_fiscal_envelopes')
        except DatabaseError as exc:assert getattr(exc.__cause__,'pgcode',None)=='42501'
        else:raise AssertionError('Customer writer must not delete documents.')
        with owner.cursor() as cursor:
            cursor.execute('SELECT COUNT(*) FROM public.customer_fiscal_envelopes');assert cursor.fetchone()[0]==1
        with source.cursor() as cursor:
            cursor.execute("SELECT pg_catalog.to_regclass('public.customer_fiscal_envelopes')");assert cursor.fetchone()[0] is None
        for sql in ['UPDATE public.customer_fiscal_envelopes SET envelope_digest=envelope_digest','DELETE FROM public.customer_fiscal_envelopes','TRUNCATE public.customer_fiscal_envelopes']:
            with owner.cursor() as cursor:cursor.execute('BEGIN')
            try:
                with owner.cursor() as cursor:cursor.execute(sql)
            except DatabaseError as exc:assert 'CUSTOMER_FISCAL_IMMUTABLE' in str(exc)
            else:raise AssertionError('Customer immutability guard did not reject mutation.')
            finally:
                with owner.cursor() as cursor:cursor.execute('ROLLBACK')
        with owner.cursor() as cursor:cursor.execute('DROP TRIGGER customer_fiscal_row_guard ON public.customer_fiscal_envelopes')
        try:store.get(document)
        except ValueError:pass
        else:raise AssertionError('Lost guards must block storage access.')
        initialize_customer_store(owner,company)
        assert store.get(document)==envelope
        # Competing first writes to a new version must create exactly one record.
        second_document=str(uuid.uuid4());second_iv=os.urandom(12);second_dek=os.urandom(32)
        second_aad=json.dumps(['sgacd-fiscal-envelope-v1','AES-256-GCM+A256KW',company,second_document,'fiscal-document'],separators=(',',':')).encode()
        second={**envelope,'context':{'company_id':company,'document_id':second_document},'iv':encode(second_iv),
                'wrapped_key':encode(aes_key_wrap(kek,second_dek)),'ciphertext':encode(AESGCM(second_dek).encrypt(second_iv,plaintext,second_aad))}
        barrier=Barrier(2)
        def replay(index):
            connection=owner.copy(alias='customer_concurrent_'+str(index));connection.settings_dict.update(USER=role,PASSWORD=password)
            try:barrier.wait(timeout=10);return CustomerPostgresStore(connection,company).put(second)['replayed']
            finally:connection.close()
        with ThreadPoolExecutor(max_workers=2) as pool:
            fs=[pool.submit(replay,index) for index in (0,1)];assert sorted(f.result(timeout=20) for f in fs)==[False,True]
        with owner.cursor() as cursor:
            cursor.execute('SELECT COUNT(*) FROM public.customer_fiscal_envelopes');assert cursor.fetchone()[0]==2
        # Revocation must affect an already-open writer, with no fallback role.
        with owner.cursor() as cursor:
            cursor.execute('REVOKE INSERT ON public.customer_fiscal_envelopes FROM '+quoted_role)
        try:store.put(envelope)
        except DatabaseError as exc:assert getattr(exc.__cause__,'pgcode',None)=='42501'
        else:raise AssertionError('Revoked INSERT must reject even an idempotent retry.')
        assert store.get(document)==envelope
        with owner.cursor() as cursor:
            cursor.execute('GRANT INSERT ON public.customer_fiscal_envelopes TO '+quoted_role)
            cursor.execute('REVOKE SELECT ON public.customer_fiscal_envelopes FROM '+quoted_role)
        try:store.get(document)
        except DatabaseError as exc:assert getattr(exc.__cause__,'pgcode',None)=='42501'
        else:raise AssertionError('Revoked SELECT must block an existing connection.')
        with owner.cursor() as cursor:
            cursor.execute('GRANT SELECT ON public.customer_fiscal_envelopes TO '+quoted_role)
        # Simulate a dropped database session, not a successful write response.
        with writer.cursor() as cursor:
            cursor.execute('SELECT pg_backend_pid()');writer_pid=cursor.fetchone()[0]
        with owner.cursor() as cursor:
            cursor.execute('SELECT pg_terminate_backend(%s)',[writer_pid]);assert cursor.fetchone()[0]
        try:store.put(envelope)
        except DatabaseError:pass
        else:raise AssertionError('Disconnected session must not report a successful write.')
        writer.close()
        assert store.put(envelope)['replayed']
        assert store.get(document)==envelope and store.get(second_document)==second
        with owner.cursor() as cursor:
            cursor.execute('SELECT COUNT(*) FROM public.customer_fiscal_envelopes');assert cursor.fetchone()[0]==2
        from customer_package_contract import run_package_contract
        package_versions,package_fixtures=run_package_contract(owner,role,password,company)
        from customer_byos_recovery import verify_customer_recovery
        recovery=verify_customer_recovery(owner,company,{document:envelope,second_document:second},packages=package_fixtures)
        return {'package_versions':package_versions,'revoked_insert_denied':True,'revoked_select_denied':True,'disconnected_session_failed_closed':True,'reconnected_retry_no_duplicate':True,'recovery':recovery,'separate_customer_database':True,'provider_destination_rejected':True,'ciphertext_only_adapter':True,
                'real_aead_roundtrip':True,'idempotent_and_concurrent_replay':True,'concurrent_first_write_single_version':True,'lost_guards_block_access':True,'overwrite_denied':True,
                'restricted_writer_delete_denied':True,'provider_has_no_document_table':True,'production_qualified':False}
    finally:
        if writer is not None:writer.close()
        with owner.cursor() as cursor:cursor.execute('DROP OWNED BY '+quoted_role)
        owner.close()
