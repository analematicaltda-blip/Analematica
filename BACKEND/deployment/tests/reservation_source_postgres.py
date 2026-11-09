"""Real PostgreSQL confirmation and revocation ordering on disposable records."""
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier, Event
from unittest.mock import patch


def run_reservation_source_races(owner):
    from django.db import connection, connections
    from django.contrib.auth import get_user_model
    from django.contrib.contenttypes.models import ContentType
    from django.utils import timezone
    from rest_framework.exceptions import PermissionDenied
    from apps.turismo.models import TourismProvider, BusinessProfile, VerifiedCompanyLink
    from apps.turismo.services.company_identity import review_link
    from apps.core_erp.outbox_models import OutboxEvent
    from apps.core_erp.tenancy.models import Tenant
    from apps.domain_business.operativa.models import Reservation
    from apps.domain_business.operativa import sargentos
    existing=set(connection.introspection.table_names());visiting=set()
    with connection.schema_editor() as editor:
        def create(model):
            model=model._meta.concrete_model
            if model._meta.db_table in existing or model in visiting:return
            visiting.add(model)
            for field in model._meta.local_fields:
                if field.is_relation and field.remote_field and field.remote_field.model is not model:create(field.remote_field.model)
            editor.create_model(model);existing.add(model._meta.db_table);visiting.remove(model)
        for model in (BusinessProfile,VerifiedCompanyLink,Reservation):create(model)
    reviewer=get_user_model()(username='source-reviewer-'+uuid.uuid4().hex,is_active=True,is_superuser=True,is_staff=True)
    get_user_model().objects.bulk_create([reviewer])
    results=[]
    for revoke in (False,True):
        tenant=Tenant.objects.create(name='Synthetic reservation source',tax_id=uuid.uuid4().hex,state='ACTIVE')
        provider=TourismProvider.objects.create(owner=owner,name='Synthetic source',provider_type='GUIDE')
        BusinessProfile.objects.create(provider=provider,legal_name='Synthetic',tax_id=tenant.tax_id,business_address='fixture',phone='fixture',email='fixture@example.test')
        link=review_link(operator=reviewer,provider_id=provider.pk,tenant_id=tenant.pk,evidence_digest='a'*64,valid_until=timezone.now()+timedelta(days=1),apply=True)
        content=ContentType.objects.get_for_model(Reservation)
        reservation=Reservation.plain_objects.create(tenant=tenant,customer_id=uuid.uuid4(),content_type=content,object_id=uuid.uuid4(),start_date=timezone.now()-timedelta(days=2),end_date=timezone.now()-timedelta(days=1),total_price='100.00')
        connections.close_all()
        def confirm():
            try:return sargentos.DomainSargentoReservas.confirm_reservation(reservation.pk,actor=owner,provider_id=provider.pk)
            except PermissionDenied:return None
            finally:connections.close_all()
        if not revoke:
            barrier=Barrier(2)
            def attempt():barrier.wait(timeout=10);return confirm()
            with ThreadPoolExecutor(max_workers=2) as pool:
                futures=[pool.submit(attempt) for _ in range(2)];rows=[f.result(timeout=25) for f in futures]
            assert sorted(row['replayed'] for row in rows)==[False,True]
            assert all(row['confirmation_event_recorded'] for row in rows)
            assert len({row['confirmation_event_id'] for row in rows})==1
            assert OutboxEvent.objects.filter(aggregate_root=str(reservation.pk),event_type=sargentos.RESERVATION_EVENT).count()==1
            reservation.refresh_from_db();assert reservation.status=='CONFIRMED'
            results.append({'scenario':'reservation_source_duplicate_confirmation','single_transition':True,'single_durable_event':True,'replayed_once':True,'ledger_written':False})
            from rest_framework.exceptions import ValidationError
            from apps.domain_business.comercial.services.reservation_fiscal import review_reservation,request_reservation_invoice,list_reservation_sources,REVIEW_EVENT
            from apps.core_erp.accounting.invoice_queue import EVENT_TYPE
            items=[{'item_id':str(uuid.uuid4()),'net':'100.00','tax':'0.00','tax_category':'EXCLUDED','policy_reference':'human-fixture-policy:1'}]
            barrier=Barrier(2)
            def review_attempt():
                try:
                    barrier.wait(timeout=10)
                    return review_reservation(actor=owner,provider_id=provider.pk,reservation_id=reservation.pk,items=items,evidence_digest='b'*64,confirmed=True,expected_revision=0)
                except ValidationError:return None
                finally:connections.close_all()
            with ThreadPoolExecutor(max_workers=2) as pool:
                futures=[pool.submit(review_attempt) for _ in range(2)];reviews=[f.result(timeout=25) for f in futures]
            accepted=[row for row in reviews if row is not None];assert len(accepted)==1
            assert OutboxEvent.objects.filter(event_type=REVIEW_EVENT,aggregate_root=str(reservation.pk)).count()==1
            results.append({'scenario':'reservation_fiscal_review_race','accepted':1,'persisted_reviews':1,'fiscal_accepted':False})
            review=accepted[0];barrier=Barrier(2)
            def request_attempt():
                try:
                    barrier.wait(timeout=10)
                    return request_reservation_invoice(actor=owner,provider_id=provider.pk,reservation_id=reservation.pk,review_id=review['review_id'],confirmed=True)
                finally:connections.close_all()
            with ThreadPoolExecutor(max_workers=2) as pool:
                futures=[pool.submit(request_attempt) for _ in range(2)];requests=[f.result(timeout=25) for f in futures]
            assert sorted(row['replayed'] for row in requests)==[False,True]
            assert OutboxEvent.objects.filter(event_type=EVENT_TYPE,aggregate_root=str(reservation.pk)).count()==1
            listed=list_reservation_sources(actor=owner,provider_id=provider.pk)['sources']
            assert len(listed)==1 and listed[0]['review_id']==review['review_id'] and listed[0]['request_created']
            results.append({'scenario':'reservation_invoice_request_race','accepted':2,'persisted_requests':1,'review_reference_preserved':True,'fiscal_accepted':False})
            from reservation_recognition_postgres import run_recognition_races
            results.extend(run_recognition_races(owner,provider,reservation,review))

        else:
            initial_read=Event();revocation_done=Event();original=sargentos.lock_company
            def paused_lock(company):
                initial_read.set()
                if not revocation_done.wait(timeout=15):raise RuntimeError('Revocation probe timed out.')
                return original(company)
            with patch.object(sargentos,'lock_company',side_effect=paused_lock):
                with ThreadPoolExecutor(max_workers=1) as pool:
                    future=pool.submit(confirm)
                    try:
                        assert initial_read.wait(timeout=15)
                        # Commit revocation after initial resolve, before lock/revalidation.
                        VerifiedCompanyLink.objects.filter(pk=link.pk).update(revoked_at=timezone.now())
                    finally:revocation_done.set()
                    assert future.result(timeout=25) is None
            reservation.refresh_from_db();assert reservation.status=='PENDING'
            assert not OutboxEvent.objects.filter(aggregate_root=str(reservation.pk)).exists()
            results.append({'scenario':'reservation_source_revoke_after_initial_read','confirmation_denied':True,'pending_preserved':True,'ledger_written':False})
    return results
