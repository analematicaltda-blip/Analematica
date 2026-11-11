"""Shared ledger primitives for independently configured backend armies.
No dependency on SGA-CD agents, models, services, desktop jobs or approval tokens.
"""
import copy,json,re,time
from dataclasses import dataclass
from datetime import date,datetime
from decimal import Decimal,Context,localcontext,ROUND_HALF_UP,InvalidOperation
from uuid import UUID,uuid5
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied,ValidationError
from .exceptions import AccountingError
from .integrity import fingerprint
from .validation import current_actor,lock_company,exact_arithmetic
from apps.core_erp.outbox_models import OutboxEvent

TASKS={'trial_balance':'Corte económico; solo asientos contabilizados',
       'integrity':'Muestra de20 asientos actuales; no certifica toda la cadena',
       'commercial_outbox':'Estado actual de transporte; no acredita aceptación DIAN',
       'profitability':'Resultado contable del intervalo solicitado',
       'quick_ratio':'Liquidez del corte; requiere clasificación revisada'}
GROUPS={'registro':('trial_balance','integrity'),
        'comercial_fiscal':('commercial_outbox',),
        'analitica':('profitability','quick_ratio')}
MAX_REPORT=24*1024

@dataclass(frozen=True)
class ArmyPolicy:
    system:str
    prefix:str
    namespace:UUID
    label:str
    groups:tuple


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)

def wire(value):
    if isinstance(value,Decimal):return format(value,'f')
    if isinstance(value,(date,UUID)):return str(value)
    if isinstance(value,dict):return {k:wire(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)):return [wire(v) for v in value]
    return value


def identifier(value):
    if not isinstance(value,str):raise ValidationError('Identificador canónico requerido.')
    try:parsed=str(UUID(value))
    except (ValueError,TypeError,AttributeError):raise ValidationError('Identificador canónico requerido.') from None
    if parsed!=value:raise ValidationError('Identificador canónico requerido.')
    return parsed


def normalize(payload):
    if not isinstance(payload,dict) or set(payload)!={'request_id','tasks','since','until','confirmed'} or payload['confirmed'] is not True:
        raise ValidationError('Contrato de misión inválido; se requiere confirmación explícita.')
    request=identifier(payload['request_id']);tasks=payload['tasks']
    if not isinstance(tasks,list) or not 1<=len(tasks)<=len(TASKS) or any(not isinstance(t,str) or t not in TASKS for t in tasks) or len(set(tasks))!=len(tasks):
        raise ValidationError('Selecciona tareas contables permitidas, sin duplicados.')
    try:
        first=date.fromisoformat(payload['since']);last=date.fromisoformat(payload['until'])
        if first.isoformat()!=payload['since'] or last.isoformat()!=payload['until'] or first>last or (last-first).days>366:raise ValueError()
    except (TypeError,ValueError):raise ValidationError('Intervalo canónico y ordenado de hasta366 días requerido.') from None
    return {'request_id':request,'tasks':sorted(tasks),'since':first.isoformat(),'until':last.isoformat()}


def hierarchy(policy):
    nodes=[{'id':policy.system+':general','rank':'GENERAL','parent':None,'name':'Jarvi · General operativo · '+policy.label,'function':'OPERATIONS'},
           {'id':policy.system+':general:neko','rank':'GENERAL','parent':None,'name':'Neko · General conversacional · '+policy.label,'function':'CONVERSATION'},
           {'id':policy.system+':general:soup','rank':'GENERAL','parent':None,'name':'SOUP · General optimizador de procesos · '+policy.label,'function':'PROCESS_OPTIMIZATION'}]
    for group,label in policy.groups:
        if group not in GROUPS:raise AccountingError('Invalid army group configuration.')
        colonel=policy.system+':coronel:'+group;captain=policy.system+':capitan:'+group
        nodes.extend([{'id':colonel,'rank':'CORONEL','parent':nodes[0]['id'],'name':'Coronel · '+label},
                      {'id':captain,'rank':'CAPITAN','parent':colonel,'name':'Capitán · '+label}])
        for task in GROUPS[group]:
            lieutenant=policy.system+':teniente:'+task;sergeant=policy.system+':sargento:'+task
            nodes.extend([{'id':lieutenant,'rank':'TENIENTE','parent':captain,'name':'Teniente · '+task},
                          {'id':sergeant,'rank':'SARGENTO','parent':lieutenant,'name':'Sargento · '+task}])
            for action in ('read','verify'):
                nodes.append({'id':policy.system+':soldado:'+task+':'+action,'rank':'SOLDADO','parent':sergeant,'name':'Soldado · '+task+' · '+action,'task':task,'tool':action})
    if len(nodes)!=29 or len({n['id'] for n in nodes})!=29:raise AccountingError('Army configuration does not cover its tasks exactly once.')
    return nodes


def task_trace(policy,task,nodes=None):
    by_id={n['id']:n for n in (nodes or hierarchy(policy))}
    chain=[];node=by_id[policy.system+':soldado:'+task+':read']
    while node:
        chain.append(node['id']);node=by_id.get(node['parent'])
    chain.reverse();chain.append(policy.system+':soldado:'+task+':verify')
    return chain


@transaction.atomic
def authority(actor,provider_id):
    from apps.turismo.services.company_identity import resolve_company
    from apps.turismo.models import TourismProvider,VerifiedCompanyLink
    if getattr(actor,'is_agent',False):raise PermissionDenied('Los agentes no heredan permisos del administrador.')
    actor=current_actor(actor)
    if getattr(actor,'is_agent',False):raise PermissionDenied('Los agentes no heredan permisos del administrador.')
    provider=identifier(str(provider_id))
    initial=resolve_company(actor,provider)
    company=lock_company(initial.tenant_id)
    TourismProvider.objects.select_for_update().get(pk=provider)
    VerifiedCompanyLink.objects.select_for_update().get(provider_id=provider)
    final=resolve_company(actor,provider)
    if final.tenant_id!=company.pk:raise PermissionDenied('El vínculo contable cambió.')
    return company,actor,provider


def read_task(task,company,request):
    first=date.fromisoformat(request['since']);last=date.fromisoformat(request['until'])
    if task=='trial_balance':
        from .reports_engine import ReportsEngine
        return ReportsEngine.get_trial_balance(company.pk,last)
    if task=='profitability':
        from .reports_engine import ReportsEngine
        return ReportsEngine.get_profitability(company.pk,first,last)
    if task=='quick_ratio':
        from .ratios import quick_ratio
        return quick_ratio(company.pk,last)
    if task=='commercial_outbox':
        from .commercial_outbox_status import inspect_commercial_outbox
        return inspect_commercial_outbox(company.pk)
    if task=='integrity':
        from .reconciliation import inspect_company
        return inspect_company(company.pk,limit=20)
    raise AccountingError('Unregistered soldier tool.')


def verify_task(task,data,company,request):
    if not isinstance(data,dict) or data.get('tenant_id',data.get('company_id'))!=str(company.pk):
        # A few core reports preserve UUID until their HTTP serialization boundary.
        if not isinstance(data,dict) or str(data.get('tenant_id',data.get('company_id')))!=str(company.pk):raise AccountingError('Soldier result scope mismatch.')
    if task=='trial_balance':
        if data.get('posted_only') is not True or data.get('valuation')!='base_currency' or data.get('cutoff_date') not in (date.fromisoformat(request['until']),request['until']):raise AccountingError('Invalid balance source.')
        debit=sum((Decimal(str(r['debit'])) for r in data['lines']),Decimal(0));credit=sum((Decimal(str(r['credit'])) for r in data['lines']),Decimal(0))
        if not debit.is_finite() or not credit.is_finite() or debit!=credit or debit!=Decimal(str(data['total_debit'])) or credit!=Decimal(str(data['total_credit'])):raise AccountingError('Soldier balance verification failed.')
        return 'VERIFIED_READ'
    if task=='profitability':
        if data.get('posted_only') is not True or data.get('currency')!=company.currency or data.get('start_date')!=request['since'] or data.get('end_date')!=request['until']:raise AccountingError('Invalid profitability source.')
        revenue,expenses,net=(Decimal(str(data[k])) for k in ('revenue','expenses','net_profit'))
        if not all(v.is_finite() for v in (revenue,expenses,net)) or revenue-expenses!=net:raise AccountingError('Invalid profitability arithmetic.')
        return 'VERIFIED_READ'
    if task=='quick_ratio':
        if data.get('currency')!=company.currency or data.get('cutoff_date')!=request['until'] or data.get('read_only') is not True:raise AccountingError('Invalid liquidity source.')
        if data.get('value') is None:
            if data.get('unavailable_reason') not in {'REVIEWED_CLASSIFICATION_REQUIRED','NON_POSITIVE_CURRENT_LIABILITIES','NEGATIVE_ACCOUNT_BALANCE_REQUIRES_REVIEW'}:raise AccountingError('Liquidity unavailable without reason.')
            return 'REQUIRES_REVIEW'
        totals={k:Decimal(str(data['totals'][k])) for k in ('cash_equivalents','temporary_investments','immediate_receivables','current_liabilities')}
        if not all(v.is_finite() and v>=0 for v in totals.values()) or totals['current_liabilities']<=0:raise AccountingError('Invalid liquidity totals.')
        expected=((totals['cash_equivalents']+totals['temporary_investments']+totals['immediate_receivables'])/totals['current_liabilities']).quantize(Decimal('0.0001'),rounding=ROUND_HALF_UP)
        if format(expected,'.4f')!=data['value'] or data.get('unavailable_reason') is not None:raise AccountingError('Liquidity verification failed.')
        return 'VERIFIED_READ'
    if task=='commercial_outbox':
        if data.get('fiscal_receipt_verified') is not False or data.get('outbox_status_is_fiscal_acceptance') is not False or data.get('ledger_written') is not False:raise AccountingError('Transport cannot certify fiscal acceptance.')
        return 'REQUIRES_REVIEW'
    if data.get('repairs_executed') is not False or data.get('full_ledger_certified') is not False:raise AccountingError('Diagnostic cannot certify or repair the ledger.')
    return 'REQUIRES_REVIEW' if (data.get('next_after') or any(r['findings'] for r in data['entries']) or data['opening_reconciliation']['status']=='REQUIRES_REVIEW') else 'VERIFIED_BOUNDED_SAMPLE'


class CommandNode:
    """Stateless live rank handler. Every order actually traverses its parents."""
    def __init__(self,node):self.node=node
    def dispatch(self,company,request,task,path,nodes,trace,position=0):
        expected=('GENERAL','CORONEL','CAPITAN','TENIENTE','SARGENTO')
        if position>=len(expected) or self.node['id']!=path[position] or self.node['rank']!=expected[position]:
            raise AccountingError('Command rank/order mismatch.')
        trace.append(self.node['id'])
        if position<4:
            child=nodes[path[position+1]]
            if child.node['parent']!=self.node['id']:raise AccountingError('Command parent mismatch.')
            return child.dispatch(company,request,task,path,nodes,trace,position+1)
        reader=nodes[path[5]];checker=nodes[path[6]]
        for soldier,tool in [(reader,'read'),(checker,'verify')]:
            if soldier.node['parent']!=self.node['id'] or soldier.node['rank']!='SOLDADO' or soldier.node['task']!=task or soldier.node['tool']!=tool:raise AccountingError('Soldier assignment mismatch.')
        trace.append(reader.node['id'])
        data=read_task(task,company,request)
        trace.append(checker.node['id'])
        try:status=verify_task(task,data,company,request)
        except (ValueError,KeyError,TypeError,InvalidOperation):raise AccountingError('Malformed soldier source.') from None
        return data,status


def dispatch_task(policy,task,company,request,nodes,trace):
    path=task_trace(policy,task,[node.node for node in nodes.values()])
    return nodes[path[0]].dispatch(company,request,task,path,nodes,trace)


class Army:
    def __init__(self,policy):
        self.policy=policy;hierarchy(policy)
    def event_id(self,company,request,kind='mission'):
        return uuid5(self.policy.namespace,str(company)+':'+identifier(request)+':'+kind)
    @exact_arithmetic
    def load(self,company,actor,provider,request):
        row=OutboxEvent.objects.filter(pk=self.event_id(company.pk,request)).first()
        if row is None:raise ValidationError('Misión no disponible en este ejército.')
        expected={'system':self.policy.system,'company_id':str(company.pk),'provider_id':provider,'actor_id':str(actor.pk),'request_id':request}
        body=row.payload
        try:
            if (row.event_type!='accounting.army.mission.v1' or row.domain!='accounting_army' or row.aggregate_root!=request or row.version!=1 or row.status!='PROCESSED'
                    or not isinstance(body,dict) or set(body)!={'scope','request','report','digest'} or body['scope']!=expected
                    or not isinstance(body['request'],dict) or normalize({**body['request'],'confirmed':True})!=body['request']):raise ValueError()
            report=body['report'];fields={'schema','system','company_id','provider_id','actor_id','request_id','since','until','results','status','ledger_written','financial_action_authorized','network_called','replayed','executed_at','human_review_required','commander'}
            if not isinstance(report,dict) or set(report)!=fields or report['schema']!='accounting-army-mission-v1':raise ValueError()
            if report['commander']!='JARVI':raise ValueError()
            if any(report[k]!=v for k,v in expected.items()) or any(report[k] is not False for k in ('ledger_written','financial_action_authorized','network_called','replayed')) or report['human_review_required'] is not True:raise ValueError()
            if any(report[k]!=body['request'][k] for k in ('since','until')) or not isinstance(report['results'],list) or [r['task'] for r in report['results']]!=body['request']['tasks']:raise ValueError()
            for result in report['results']:
                if type(result.get('duration_ns')) is not int or not 0<=result['duration_ns']<=10**15:raise ValueError()
                if result['scope']!=TASKS[result['task']] or not isinstance(result['trace'],list) or not 1<=len(result['trace'])<=7 or result['trace']!=task_trace(self.policy,result['task'])[:len(result['trace'])]:raise ValueError()
                if result['status']!='BLOCKED' and len(result['trace'])!=7:raise ValueError()
                if result['status']=='BLOCKED':
                    if set(result)!={'task','status','code','scope','trace','data','data_digest','duration_ns'} or result['code']!='ACCOUNTING_PRECONDITION' or result['data'] is not None or result['data_digest'] is not None:raise ValueError()
                elif (set(result)!={'task','status','source','scope','trace','data','data_digest','duration_ns'} or result['source']!=result['task']
                      or fingerprint(result['data'])!=result['data_digest'] or verify_task(result['task'],result['data'],company,body['request'])!=result['status']):raise ValueError()
            status='COMPLETED_READ' if all(r['status']=='VERIFIED_READ' for r in report['results']) else 'REQUIRES_REVIEW'
            if report['status']!=status or len(canonical(report).encode())>MAX_REPORT:raise ValueError()
            moment=datetime.fromisoformat(report['executed_at'])
            if moment.tzinfo is None or moment>timezone.now():raise ValueError()
            if fingerprint({'scope':body['scope'],'request':body['request'],'report':body['report']})!=body['digest']:raise ValueError()
        except (ValueError,TypeError,KeyError,AttributeError,ValidationError):
            raise AccountingError('Persisted mission changed.') from None
        return body
    @transaction.atomic
    def catalog(self,actor,provider_id):
        company,actor,provider=authority(actor,provider_id)
        return {'schema':'accounting-army-catalog-v1','system':self.policy.system,'company_id':str(company.pk),'provider_id':provider,
                'nodes':hierarchy(self.policy),'tasks':dict(TASKS),'logical_agents':29,'execution':'BOUNDED_DETERMINISTIC_HIERARCHY',
                'ledger_written':False,'financial_action_authorized':False,'external_engine_required':False}
    @transaction.atomic
    def run(self,actor,provider_id,payload):
        request=normalize(payload)
        with localcontext(Context(prec=50)):
            company,actor,provider=authority(actor,provider_id)
            existing=OutboxEvent.objects.filter(pk=self.event_id(company.pk,request['request_id'])).exists()
            if existing:
                old=self.load(company,actor,provider,request['request_id'])
                if old['request']!=request:raise AccountingError('Request ID already binds a different mission.')
                return {**copy.deepcopy(old['report']),'replayed':True}
            results=[];nodes={node['id']:CommandNode(node) for node in hierarchy(self.policy)}
            for task in request['tasks']:
                chain=[]
                started=time.perf_counter_ns()
                try:
                    with transaction.atomic():
                        data,status=dispatch_task(self.policy,task,company,request,nodes,chain)
                        data=wire(data)
                        if len(canonical(data).encode())>MAX_REPORT:raise AccountingError('Task result exceeds mission bound.')
                    results.append({'task':task,'status':status,'source':task,'scope':TASKS[task],
                                    'trace':chain,'data':data,'data_digest':fingerprint(data),'duration_ns':time.perf_counter_ns()-started})
                except AccountingError:
                    results.append({'task':task,'status':'BLOCKED','code':'ACCOUNTING_PRECONDITION','scope':TASKS[task],'trace':chain,'data':None,'data_digest':None,'duration_ns':time.perf_counter_ns()-started})
            # Revalidate identity before persisting/releasing any report.
            if authority(actor,provider)[0].pk!=company.pk:raise PermissionDenied('El vínculo cambió durante la misión.')
            report={'schema':'accounting-army-mission-v1','system':self.policy.system,'company_id':str(company.pk),
                    'provider_id':provider,'actor_id':str(actor.pk),'request_id':request['request_id'],
                    'since':request['since'],'until':request['until'],'results':results,
                    'status':'COMPLETED_READ' if all(r['status']=='VERIFIED_READ' for r in results) else 'REQUIRES_REVIEW',
                    'ledger_written':False,'financial_action_authorized':False,'network_called':False,'replayed':False,
                    'executed_at':timezone.now().isoformat(),'human_review_required':True,'commander':'JARVI'}
            if len(canonical(report).encode())>MAX_REPORT:raise AccountingError('Combined mission report exceeds its bound.')
            scope={'system':self.policy.system,'company_id':str(company.pk),'provider_id':provider,'actor_id':str(actor.pk),'request_id':request['request_id']}
            body={'scope':scope,'request':request,'report':report,'digest':fingerprint({'scope':scope,'request':request,'report':report})}
            OutboxEvent.objects.create(id=self.event_id(company.pk,request['request_id']),event_type='accounting.army.mission.v1',domain='accounting_army',aggregate_root=request['request_id'],payload=body,version=1,status='PROCESSED')
            return report
    @transaction.atomic
    def state(self,actor,provider_id,request_id):
        request=identifier(request_id);company,actor,provider=authority(actor,provider_id)
        return copy.deepcopy(self.load(company,actor,provider,request)['report'])
    def plan(self,actor,provider_id,request_id):
        report=self.state(actor,provider_id,request_id)
        return {'schema':'accounting-army-engine-plan-v1','system':self.policy.system,
                'ranks':['GENERAL','CORONEL','CAPITAN','TENIENTE','SARGENTO','SOLDADO'],
                'tasks':[{'id':r['task'],'status':r['status']} for r in report['results']],
                'financial_actions_allowed':False,'tools_allowed':[],
                'instruction':'Planifica revisión humana. No publiques, no firmes, no contabilices ni ejecutes dinero.'}

    def engine_plan(self,actor,provider_id,request_id,engine,payload,adapter):
        from .agent_army_engines import configuration,EngineUnavailable,EngineOutcomeUnknown
        if not isinstance(payload,dict) or set(payload)!={'confirmed','share_plan'} or payload['confirmed'] is not True or payload['share_plan'] is not True:raise ValidationError('Confirma expresamente compartir solo el plan, sin datos financieros.')
        if engine not in ('open-duet','agent-desktop'):raise ValidationError('Motor no permitido.')
        request=identifier(request_id)
        with transaction.atomic():
            company,actor,provider=authority(actor,provider_id)
            mission=self.load(company,actor,provider,request)
            plan=self.plan(actor,provider,request)
            key=self.event_id(company.pk,request,'engine:'+engine)
            old=OutboxEvent.objects.filter(pk=key).first()
            scope=mission['scope'];plan_digest=fingerprint(plan)
            if old:
                if old.event_type!='accounting.army.engine.reserved.v1' or old.domain!='accounting_army' or old.aggregate_root!=request or old.status!='PROCESSED' or old.version!=1 or old.payload!={'scope':scope,'engine':engine,'plan_digest':plan_digest}:raise AccountingError('Engine reservation changed.')
                done=OutboxEvent.objects.filter(pk=self.event_id(company.pk,request,'result:'+engine)).first()
                if done:
                    body=done.payload
                    if done.event_type!='accounting.army.engine.result.v1' or done.domain!='accounting_army' or done.aggregate_root!=request or done.status!='PROCESSED' or done.version!=1 or not isinstance(body,dict) or set(body)!={'scope','engine','plan_digest','result','digest'} or body['scope']!=scope or body['engine']!=engine or body['plan_digest']!=plan_digest or fingerprint(body['result'])!=body['digest']:raise AccountingError('Engine result changed.')
                    return {**copy.deepcopy(body['result']),'replayed':True}
                return {'engine':engine,'state':'OUTCOME_UNKNOWN','auto_retry':False,'replayed':True,'financial_action_authorized':False}
            configuration(self.policy,actor,company,engine)
            OutboxEvent.objects.create(id=key,event_type='accounting.army.engine.reserved.v1',domain='accounting_army',aggregate_root=request,
                payload={'scope':scope,'engine':engine,'plan_digest':plan_digest},version=1,status='PROCESSED')
        # External engine calls never hold a ledger/company transaction lock.
        try:result=adapter(actor,company,engine,plan)
        except (EngineUnavailable,EngineOutcomeUnknown):result={'engine':engine,'state':'OUTCOME_UNKNOWN','auto_retry':False,'financial_action_authorized':False}
        if not isinstance(result,dict) or result.get('engine')!=engine or result.get('financial_action_authorized') is not False:raise EngineOutcomeUnknown('Invalid engine result.')
        with transaction.atomic():
            current,actor,provider=authority(actor,provider)
            self.load(current,actor,provider,request)
            OutboxEvent.objects.create(id=self.event_id(current.pk,request,'result:'+engine),event_type='accounting.army.engine.result.v1',
                domain='accounting_army',aggregate_root=request,payload={'scope':scope,'engine':engine,'plan_digest':plan_digest,'result':result,'digest':fingerprint(result)},version=1,status='PROCESSED')
        return {**result,'replayed':False}
