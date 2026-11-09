"""Actual PostgreSQL row-lock races for the internal invoice-request service."""
import copy,uuid
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

def run_invoice_queue_races(user):
    from django.db import connections
    from apps.core_erp.tenancy.models import Tenant
    from apps.core_erp.outbox_models import OutboxEvent
    from apps.core_erp.accounting.invoice_queue import enqueue_invoice_intent
    results=[]
    for conflict in (False,True):
        tenant=Tenant.objects.create(name='Synthetic invoice-request company',tax_id=uuid.uuid4().hex,state='ACTIVE')
        value={'schema':'sgacd-invoice-intent-v1','company_id':str(tenant.pk),'source_type':'reservation','source_id':str(uuid.uuid4()),'revision':1,'state':'CONFIRMED','currency':'COP','items':[{'item_id':str(uuid.uuid4()),'net':'100.00','tax':'19.00','tax_category':'TAXABLE','policy_reference':'fixture-policy:1'}]}
        connections.close_all();barrier=Barrier(2)
        def attempt(index):
            snapshot=copy.deepcopy(value)
            if conflict and index:snapshot['items'][0]['net']='200.00'
            try:
                barrier.wait(timeout=10)
                return enqueue_invoice_intent(snapshot,company_id=tenant.pk,actor=user)
            except ValueError:return None
            finally:connections.close_all()
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(attempt,i) for i in (0,1)];outcomes=[f.result(timeout=25) for f in futures]
        accepted=[r for r in outcomes if r is not None]
        assert len(accepted)==(1 if conflict else 2)
        rows=OutboxEvent.objects.filter(aggregate_root=value['source_id'])
        assert rows.count()==1 and rows.get().status=='PENDING'
        if not conflict:assert sorted(r['replayed'] for r in accepted)==[False,True]
        results.append({'scenario':'invoice_queue_changed_payload' if conflict else 'invoice_queue_duplicate',
                        'accepted':len(accepted),'persisted_requests':1,'published':False,'fiscal_accepted':False})
    return results
