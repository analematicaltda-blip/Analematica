"""Jarvi, Neko and SOUP behavior primitives; local staff live in each backend."""
from decimal import Decimal,Context,localcontext
from rest_framework.exceptions import ValidationError
from django.db import transaction
from .agent_army_runtime import Army,authority,normalize,fingerprint

class JarviOperationalGeneral(Army):
    def execute_mission(self,actor,provider_id,mission):
        return self.run(actor,provider_id,mission)

class NekoConversationalGeneral:
    def __init__(self,jarvi):self.jarvi=jarvi
    @transaction.atomic
    def preview(self,actor,provider_id,payload):
        if not isinstance(payload,dict) or set(payload)!={'request_id','question','since','until','modality'} or payload['modality'] not in ('TEXT','VOICE_TRANSCRIPT'):
            raise ValidationError('Solicitud de Neko inválida; texto o transcripción explícita requeridos.')
        question=payload['question']
        from .query_assistant import resolve_question
        try:
            if question in ('balance de comprobación','balance de prueba'):task='trial_balance'
            elif question in ('diagnóstico de integridad','integridad contable'):task='integrity'
            else:task={'commercial_queue':'commercial_outbox','quick_ratio':'quick_ratio','profitability':'profitability'}[resolve_question(question)]
        except (ValueError,TypeError,KeyError):raise ValidationError('Solicitud no soportada; no se delegó una operación por defecto.') from None
        request=normalize({'request_id':payload['request_id'],'tasks':[task],'since':payload['since'],'until':payload['until'],'confirmed':True})
        company,actor,provider=authority(actor,provider_id)
        return {'schema':'accounting-neko-preview-v1','system':self.jarvi.policy.system,'interpreter':'NEKO','interpreter_rank':'GENERAL_CONVERSACIONAL','commander':'JARVI',
                'draft':{**request,'confirmed':False},'preview_digest':fingerprint({'company_id':str(company.pk),'actor_id':str(actor.pk),'request':request}),
                'confirmation_required':True,'modality':payload['modality'],'voice_is_approval':False,
                'mission_executed':False,'ledger_written':False,'financial_action_authorized':False}

class SoupProcessOptimizerGeneral:
    def __init__(self,jarvi):self.jarvi=jarvi
    def evaluate(self,actor,provider_id,request_id):
        report=self.jarvi.state(actor,provider_id,request_id)
        rows=report['results'];recommendations=[]
        for row in rows:
            if row['status']=='BLOCKED':recommendations.append({'task':row['task'],'code':'RESOLVE_PRECONDITION','automatic_change_allowed':False})
            elif row['status']=='REQUIRES_REVIEW':recommendations.append({'task':row['task'],'code':'REVIEW_SOURCE_OR_POLICY','automatic_change_allowed':False})
            if row['duration_ns']>250000000:recommendations.append({'task':row['task'],'code':'PROFILE_READ_LATENCY','automatic_change_allowed':False})
        with localcontext(Context(prec=50)):
            total=sum(r['duration_ns'] for r in rows)
            return {'schema':'accounting-soup-evaluation-v1','system':self.jarvi.policy.system,'optimizer':'SOUP','optimizer_rank':'GENERAL_OPTIMIZADOR_DE_PROCESOS','commander':'JARVI',
                'request_id':report['request_id'],'mission_executed_at':report['executed_at'],
                'task_samples':[{'task':r['task'],'duration_ns':r['duration_ns'],'status':r['status']} for r in rows],
                'total_tool_duration_ns':total,'total_tool_duration_ms':format(Decimal(total)/Decimal(1000000),'f'),
                'recommendations':recommendations,'quality_scope':'Observed deterministic tool execution, not model accuracy or end-to-end SLA',
                'training_executed':False,'candidate_activated':False,'activation_allowed':False,'backend_72_tests_passed':None,
                'ledger_written':False,'financial_action_authorized':False,'architect_review_required':True}
