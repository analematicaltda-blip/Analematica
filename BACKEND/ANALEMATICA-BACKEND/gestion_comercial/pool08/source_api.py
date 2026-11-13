"""Signed source ingress still requires the mapped native owner's authenticated session."""
from datetime import datetime,timezone
import copy,json
from rest_framework.parsers import BaseParser
from rest_framework.response import Response
from .api import Pool08View
from .crm import CRMError,digest
from .access_protocol import AccessFault
from .source_protocol import verify,acknowledge
from .source_binding import binding
from .sales_operations import Operations
from .sales import Sales
from .sales_store import Store
from .sales_ledger import Ledger
from .sales_models import SaleSourceBinding

class SourceParser(BaseParser):
    media_type='application/json'
    def parse(self,stream,media_type=None,parser_context=None):
        raw=stream.read(262145)
        if len(raw)>262144:raise CRMError('BODY_LIMIT',413)
        def pairs(items):
            result={}
            for key,value in items:
                if key in result:raise ValueError()
                result[key]=value
            return result
        def constant(value):raise ValueError()
        try:return json.loads(raw,object_pairs_hook=pairs,parse_constant=constant)
        except (ValueError,UnicodeError,RecursionError):raise CRMError('INVALID_JSON',400) from None

class ExternalOperations(Operations):
    def __init__(self,quotes,proof):super().__init__(quotes);self.proof=proof
    def validate(self,source,data,fact):
        result=self.labor(source,data,fact);proof=self.proof
        if not isinstance(proof,dict) or set(proof)!={'plan_digest','valid','operation_refs','reserved','requires_capacity'} or proof['valid'] is not True:raise CRMError('SOURCE_OPERATION_REVIEW_REQUIRED')
        
        import re
        if not isinstance(proof['plan_digest'],str) or not re.fullmatch('[a-f0-9]{64}',proof['plan_digest']) or type(proof['reserved'])!=bool or type(proof['requires_capacity'])!=bool or not isinstance(proof['operation_refs'],list) or len(proof['operation_refs'])>10:raise CRMError('INVALID_SOURCE_OPERATION_PROOF')
        result['source_operation_plan_digest']=proof['plan_digest'];return result
    def reserve(self,item):
        if self.proof['requires_capacity'] and self.proof['reserved'] is not True:raise CRMError('SOURCE_CAPACITY_RESERVATION_REQUIRED',409)
        return copy.deepcopy(self.proof['operation_refs'])
    def release(self,item):pass # Native acknowledgment authorizes SGA's subsequent local release, never claims atomicity.

def verify_financial_state(engine,sale):
    if sale.get('journal'):
        engine.ledger.verify(sale)
    if sale.get('reversal'):
        from apps.core_erp.accounting.models import JournalEntry
        from apps.core_erp.accounting.ledger_engine import LedgerEngine
        row=JournalEntry.plain_objects.filter(pk=sale['reversal']['id'],tenant_id=engine.store.scope,is_posted=True,is_reversal=True,reversed_entry_id=sale['journal']['id']).first()
        if not row or row.system_hash!=sale['reversal']['hash'] or LedgerEngine.calculate_hash(row)!=row.system_hash:raise CRMError('SALE_JOURNAL_INTEGRITY_REQUIRED',503)

class SaleSourceView(Pool08View):
    parser_classes=[SourceParser]
    def handle_exception(self,exc):
        if isinstance(exc,(CRMError,AccessFault)):return Response({'code':str(exc)},status=exc.status)
        from apps.core_erp.accounting.exceptions import AccountingError
        if isinstance(exc,AccountingError):return Response({'code':'SALE_ACCOUNTING_REVIEW_REQUIRED'},status=409)
        return super().handle_exception(exc)
    def post(self,request,action):
        from .crm_api import CRMView,make_quotations
        context,body=verify(request.data)
        if not isinstance(body,dict):raise CRMError('INVALID_SOURCE_COMMAND')
        if action=='scopes':
            if body!={}:raise CRMError('INVALID_SOURCE_COMMAND')
            from .identity import resolve_access
            result=[]
            for row in SaleSourceBinding.objects.filter(source_system='sga-cd',source_scope=context['scope'],source_actor=context['actor'],actor_ref=str(request.user.pk),revoked_at=None,valid_until__gt=datetime.now(timezone.utc))[:100]:
                try:
                    from types import SimpleNamespace
                    from django.http import QueryDict
                    q=QueryDict('',mutable=True);q['provider_id']=row.provider_ref;crm=CRMView().service(SimpleNamespace(user=request.user,query_params=q,method='POST'));binding(context,crm);result.append({'provider_id':row.provider_ref,'company_id':row.tenant_ref,'name':crm.store.company_name,'binding_id':str(row.pk)})
                except (CRMError,AccessFault):continue
            return Response(acknowledge(context,{'scopes':result}))
        crm=CRMView().service(request);linked=binding(context,crm);quotes=make_quotations(crm);store=Store(crm.store)
        if action=='after-sales':
            from .after_sales import execute
            if body.get('operation')=='followup':raise CRMError('LOCAL_CRM_FOLLOWUP_REQUIRED')
            if set(body)!={'operation','data'}:raise CRMError('INVALID_SOURCE_COMMAND')
            return Response(acknowledge(context,execute(crm,request.user,body['operation'],body['data'])))
        if action=='accounts' and body!={}:raise CRMError('INVALID_SOURCE_COMMAND')
        if action=='accounts':return Response(acknowledge(context,{'accounts':Ledger(crm).catalog(),'binding_id':str(linked.pk)}))
        if set(body)-{'command','source','operation_proof','sale_id'}:raise CRMError('INVALID_SOURCE_COMMAND')
        source=copy.deepcopy(body.get('source'))
        if action in ('state','analytics'):
            if set(body)!={'sale_id'}:raise CRMError('INVALID_SOURCE_COMMAND')
            sale=store.get(body['sale_id'])
            if not sale or sale['source'].get('_external')!={'system':'sga-cd','scope':context['scope'],'actor':context['actor'],'binding_id':str(linked.pk)}:raise CRMError('SOURCE_SALE_NOT_FOUND',404)
            engine=Sales(store,quotes,Ledger(crm),ExternalOperations(quotes,{}));engine.get(sale['id']);verify_financial_state(engine,sale)
            result={'sale':sale,'binding_id':str(linked.pk)}
            if action=='analytics':
                from .analytics_sources import income
                result['economics']=income(crm,[sale])
            return Response(acknowledge(context,result))
        if action!='command' or set(body)!={'command','source','operation_proof'} or not isinstance(source,dict):raise CRMError('INVALID_SOURCE_COMMAND')
        if set(source)!={'quotation_id','version','content_digest','content','acceptance'} or not isinstance(source['content'],dict) or not isinstance(source['acceptance'],dict) or source['acceptance'].get('content_digest')!=source['content_digest'] or digest(source['content'])!=source['content_digest']:raise CRMError('INVALID_SOURCE_QUOTATION')
        marker={'system':'sga-cd','scope':context['scope'],'actor':context['actor'],'binding_id':str(linked.pk)};source['_external']=marker
        ops=ExternalOperations(quotes,body['operation_proof']);engine=Sales(store,quotes,Ledger(crm),ops)
        def source_reader(ref):
            if ref!=source['quotation_id']:raise CRMError('SOURCE_QUOTE_MISMATCH',409)
            return source
        engine.source=source_reader
        command=body['command']
        if not isinstance(command,dict):raise CRMError('INVALID_SOURCE_COMMAND')
        if command.get('sale_id'):
            current=engine.get(command['sale_id'])
            if current['source'].get('_external')!=marker or current['source']['content_digest']!=source['content_digest']:raise CRMError('SOURCE_QUOTE_MISMATCH',409)
        receipt=engine.command(command);sale=engine.get(receipt['sale_id']);verify_financial_state(engine,sale);return Response(acknowledge(context,{'receipt':receipt,'sale':sale,'binding_id':str(linked.pk)}))
