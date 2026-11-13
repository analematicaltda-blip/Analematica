"""Own operational capacity and existing SG-SST/payroll gates; no synthetic dispatch."""
import uuid
from datetime import datetime,timezone,timedelta
from decimal import Decimal
from .crm import CRMError,digest,moment,text
from .opportunities import uuid_ref
class Operations:
    def __init__(self,quotes):self.quotes=quotes;self.crm=quotes.crm;self.provider=self.crm.store.provider
    def labor(self,source,data,fact):
        if not isinstance(data,dict) or not {'mode','order_id','reason','support_digest'}<=set(data) or set(data)-{'mode','order_id','reason','support_digest','cost_since','cost_until'} or data['mode'] not in ('NO_LABOR_REVIEWED','EXISTING_LABOR_ORDER'):raise CRMError('OPERATION_REVIEW_REQUIRED')
        import re
        text(data['reason'],500)
        if not isinstance(data['support_digest'],str) or not re.fullmatch('[a-f0-9]{64}',data['support_digest']):raise CRMError('OPERATION_SUPPORT_REQUIRED')
        result={'mode':data['mode'],'support_digest':data['support_digest'],'physical_execution_verified':False,'labor_cost_posted':False}
        if data['mode']=='NO_LABOR_REVIEWED':
            if data['order_id'] is not None:raise CRMError('UNEXPECTED_LABOR_ORDER')
        else:
            from apps.prestadores.mi_negocio.gestion_operativa.dispatch_authorization import dispatch_state
            from apps.prestadores.mi_negocio.gestion_contable.nomina.operational_costs import operation_cost_report
            uuid_ref(data['order_id']);state=dispatch_state(actor_id=self.crm.actor,provider_id=self.provider,order_id=data['order_id'])
            if not state.get('dispatch_recorded') or state.get('source_changed_since_dispatch'):raise CRMError('SST_DISPATCH_REQUIRED',409)
            if fact=='SERVICE_DELIVERED':
                if not state.get('recorded_end') or moment(state['recorded_end'])>datetime.now(timezone.utc):raise CRMError('LABOR_COMPLETION_REQUIRED',409)
                from django.contrib.auth import get_user_model
                if not isinstance(data.get('cost_since'),str) or not isinstance(data.get('cost_until'),str):raise CRMError('LABOR_COST_WINDOW_REQUIRED')
                from datetime import date
                try:
                    start,end=date.fromisoformat(data['cost_since']),date.fromisoformat(data['cost_until'])
                    if start.isoformat()!=data['cost_since'] or end.isoformat()!=data['cost_until'] or start>end or (end-start).days>366:raise ValueError()
                except (ValueError,TypeError):raise CRMError('INVALID_LABOR_COST_WINDOW') from None
                report=operation_cost_report(actor=get_user_model().objects.get(pk=self.crm.actor),provider_id=self.provider,order_id=data['order_id'],since=data['cost_since'],until=data['cost_until'])
                if not report['source_complete'] or not report['lines']:raise CRMError('REVIEWED_PAYROLL_COST_REQUIRED',409)
                result.update(labor_cost_posted=True,labor_cost_digest=digest(report))
            result['dispatch_id']=state['dispatch_id'];result['order_id']=data['order_id']
        return result
    def validate(self,source,data,fact):
        result=self.labor(source,data,fact)
        content=source['content']
        for line in content['estimate']['lines']:self.quotes.policy(line['item_id'],line['revision'])
        if fact=='UNCONDITIONAL_RECEIVABLE':
            refs=sorted({self.quotes.policy(line['item_id'],line['revision'])['resource_ref'] for line in content['estimate']['lines'] if self.quotes.policy(line['item_id'],line['revision'])['mode']=='REQUIRED'})
            for ref in refs:self.quotes.capacity.models().objects.select_for_update().get(pk=ref,provider_id=self.provider)
            result['capacity_check']=self.quotes.inspect_capacity(content)
        elif any(moment(w['end_at'])>datetime.now(timezone.utc) for w in content['service_windows']):raise CRMError('SERVICE_NOT_DELIVERED_YET',409)
        # Stable evidence, no changing clock in the financial review fingerprint.
        if 'capacity_check' in result:
            result['capacity_check'].pop('checked_at',None)
            for check in result['capacity_check']['checks']:check.pop('checked_at',None)
        return result
    def reserve(self,item):
        if item['review']['terms']['economic_fact']!='UNCONDITIONAL_RECEIVABLE':return []
        from apps.turismo.models import AvailabilityHold
        result=[];source=item['source'];windows={x['item_id']:x for x in source['content']['service_windows']}
        for line in source['content']['estimate']['lines']:
            policy=self.quotes.policy(line['item_id'],line['revision'])
            if policy['mode']=='NOT_APPLICABLE':continue
            w=windows[line['item_id']];row=self.quotes.capacity.resource(policy['resource_ref']);identifier=uuid.uuid5(uuid.NAMESPACE_URL,'commercial-sale-hold:'+item['id']+':'+line['item_id'])
            hold=AvailabilityHold.objects.create(id=identifier,provider_id=self.provider,service=row,requested_by_id=self.crm.actor,idempotency_key=identifier,request_digest=digest({'sale':item['id'],'window':w,'line':line}),start_at=moment(w['start_at']),end_at=moment(w['end_at']),quantity=int(Decimal(line['quantity'])),expires_at=moment(w['end_at']))
            result.append({'hold_id':str(hold.pk),'resource_ref':str(row.pk),'quantity':hold.quantity,'end_at':hold.end_at.isoformat()})
        return result
    def release(self,item):
        from apps.turismo.models import AvailabilityHold
        from apps.core_erp.accounting.commercial_sales_guard import permit
        with permit(self.crm.store.scope,item['id']):
            for ref in item['operation_refs']:
                row=AvailabilityHold.objects.select_for_update().filter(pk=ref['hold_id'],provider_id=self.provider,requested_by_id=self.crm.actor).first()
                if not row or row.released_at is not None:raise CRMError('SALE_HOLD_RECONCILIATION_REQUIRED',409)
                row.released_at=datetime.now(timezone.utc);row.save(update_fields=['released_at'])
