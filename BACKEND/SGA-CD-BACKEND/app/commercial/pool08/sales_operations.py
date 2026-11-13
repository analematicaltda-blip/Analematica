"""Durable SGA space claims. Release requires a verified native terminal outcome."""
from datetime import datetime,timezone
from decimal import Decimal
import uuid
from .crm import CRMError,digest,moment,text
from .sales_models import SaleSpaceClaim
from .sales_space_guards import require
from .quotation_capacity import Capacity
from app.models.academic import Reserva
class Operations:
    def __init__(self,quotes):self.quotes=quotes;self.crm=quotes.crm;self.db=quotes.crm.store.db
    def validate(self,source,data,fact,refs=None):
        if not isinstance(data,dict) or not {'mode','order_id','reason','support_digest'}<=set(data) or data['mode'] not in ('NO_LABOR_REVIEWED','EXISTING_LABOR_ORDER'):raise CRMError('OPERATION_REVIEW_REQUIRED')
        import re
        text(data['reason'],500)
        if not isinstance(data['support_digest'],str) or not re.fullmatch('[a-f0-9]{64}',data['support_digest']):raise CRMError('OPERATION_SUPPORT_REQUIRED')
        windows={x['item_id']:x for x in source['content']['service_windows']};groups={};policies=[]
        for line in source['content']['estimate']['lines']:
            policy=self.quotes.policy(line['item_id'],line['revision']);policies.append({'id':policy['id'],'digest':policy['last_event_digest']})
            if policy['mode']=='NOT_APPLICABLE':continue
            w=windows.get(line['item_id']);q=Decimal(line['quantity'])
            if not w or q!=q.to_integral_value():raise CRMError('SALE_OPERATION_WINDOW_REQUIRED')
            start,end=moment(w['start_at']),moment(w['end_at'])
            if fact=='SERVICE_DELIVERED':
                if end>datetime.now(timezone.utc):raise CRMError('SERVICE_NOT_DELIVERED_YET',409)
                continue
            if start<=datetime.now(timezone.utc):raise CRMError('SALE_OPERATION_ALREADY_STARTED',409)
            groups.setdefault(policy['resource_ref'],[]).append((start,end,int(q)))
        plans=[]
        for resource,ranges in sorted(groups.items()):
            self.quotes.capacity.resource(resource);events=[]
            for start,end,q in ranges:events.extend([(start,q),(end,-q)])
            active=peak=0
            for _,n in sorted(events,key=lambda x:(x[0],x[1])):active+=n;peak=max(peak,active)
            first,last=min(x[0] for x in ranges),max(x[1] for x in ranges);plans.append({'resource_ref':resource,'start_at':first.isoformat(),'end_at':last.isoformat(),'quantity':peak})
        if refs:
            for plan in plans:
                ref=next((x for x in refs if x['resource_ref']==plan['resource_ref']),None)
                if not ref:raise CRMError('SALE_SPACE_CLAIM_REQUIRED',409)
                claim=self.db.query(SaleSpaceClaim).filter_by(id=ref['claim_id'],scope=self.crm.store.scope,released=False).first();row=self.db.get(Reserva,ref['sga_reservation_id'])
                if not claim or not row or claim.reservation_id!=row.id or row.inquilino_id!=self.crm.store.tenant or row.escenario_parte_id!=int(plan['resource_ref']) or self.stamp(row.fecha_inicio)!=plan['start_at'] or self.stamp(row.fecha_fin)!=plan['end_at']:raise CRMError('SALE_SPACE_CLAIM_CHANGED',409)
        else:
            for plan in plans:
                result=self.quotes.capacity.inspect(plan['resource_ref'],moment(plan['start_at']),moment(plan['end_at']),plan['quantity'])
                if not result['available']:raise CRMError('CAPACITY_NOT_AVAILABLE',409)
        return {'plan_digest':digest({'plans':plans,'policies':policies,'fact':fact,'operation':data}),'valid':True,'operation_refs':refs or [],'reserved':bool(refs) or not plans,'requires_capacity':bool(plans),'plans':plans}
    def stamp(self,value):return (value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)).isoformat()
    def reserve(self,item):
        proof=self.validate(item['source'],item['review']['terms']['operation'],item['review']['terms']['economic_fact']);refs=[]
        if proof['plans']:require(self.db)
        for plan in proof['plans']:
            row=Reserva(inquilino_id=self.crm.store.tenant,escenario_parte_id=int(plan['resource_ref']),usuario_id_reserva=int(self.crm.actor),proposito='Venta '+item['id'],fecha_inicio=moment(plan['start_at']),fecha_fin=moment(plan['end_at']),estado='Pendiente contable');self.db.add(row);self.db.flush();claim=SaleSpaceClaim(id=str(uuid.uuid4()),scope=self.crm.store.scope,sale_id=item['id'],reservation_id=row.id,released=False);self.db.add(claim);self.db.flush();refs.append({**plan,'claim_id':claim.id,'sga_reservation_id':row.id})
        return refs
    def confirm(self,item):
        for ref in item['operation_refs']:
            row=self.db.get(Reserva,ref['sga_reservation_id'])
            claim=self.db.query(SaleSpaceClaim).filter_by(id=ref['claim_id'],scope=self.crm.store.scope,sale_id=item['id'],reservation_id=ref['sga_reservation_id'],released=False).first()
            if not row or not claim or row.inquilino_id!=self.crm.store.tenant:raise CRMError('SALE_SPACE_CLAIM_CHANGED',409)
            row.estado='Confirmada'
        self.db.flush()
    def release(self,item):
        for ref in item['operation_refs']:
            claim=self.db.query(SaleSpaceClaim).filter_by(id=ref['claim_id'],scope=self.crm.store.scope,sale_id=item['id'],released=False).first()
            if not claim or claim.reservation_id!=ref['sga_reservation_id']:raise CRMError('SALE_SPACE_CLAIM_CHANGED',409)
            claim.released=True;self.db.flush();row=self.db.get(Reserva,ref['sga_reservation_id'])
            if row:row.estado='Cancelada'
        self.db.flush()
