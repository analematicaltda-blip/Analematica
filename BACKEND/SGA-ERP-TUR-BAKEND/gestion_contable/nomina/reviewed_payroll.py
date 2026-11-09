"""Bounded COP base-pay accrual; declared rules, not statutory payroll certification.
Two persisted owner confirmations. No default rates, bank payment or DIAN call.
"""
from datetime import date
import re
from uuid import UUID, uuid5
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from apps.turismo.models import TourismProvider
from apps.turismo.services.company_identity import resolve_company
from apps.core_erp.accounting.validation import current_actor, lock_company
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.invoice_intent import _money, _format_money
from apps.core_erp.accounting.integrity import fingerprint
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.accounting.models import Account, FiscalPeriod, JournalEntry, AccountingEventReceipt, LedgerEntry
from apps.core_erp.outbox_models import OutboxEvent
from .models import Planilla, Empleado, Contrato, NovedadNomina, DetalleLiquidacion, Ausencia, IncapacidadLaboral

NS = UUID('048a19d8-1857-46d1-aaea-a155d6245ae2')
REVIEW = 'accounting.payroll.reviewed.v1'
APPLIED = 'accounting.payroll.applied.v1'
POLICY = 'accounting.payroll.policy-declared.v1'
KINDS = {'EMPLOYEE_DEDUCTION', 'EMPLOYER_CONTRIBUTION', 'PROVISION'}
ACCOUNT_TYPES = {'salary_expense':'EXPENSE','employee_payable':'LIABILITY',
                 'deductions_payable':'LIABILITY','employer_expense':'EXPENSE',
                 'employer_payable':'LIABILITY','provision_expense':'EXPENSE',
                 'provision_payable':'LIABILITY'}

def _digest(value):
    if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{64}',value):
        raise AccountingError('Explicit evidence digest required.')
    return value

def _context(actor, provider_id, payroll_id):
    user = current_actor(actor)
    if getattr(user,'is_agent',False):raise PermissionDenied('Se requiere un titular personal.')
    provider = TourismProvider.objects.select_for_update().filter(pk=UUID(str(provider_id)),owner_id=user.pk,is_active=True,status='ACTIVE').first()
    if provider is None:raise PermissionDenied('Empresa no autorizada.')
    company = resolve_company(user,provider.pk).tenant
    company=lock_company(company.pk)
    user=current_actor(user)
    if getattr(user,'is_agent',False):raise PermissionDenied('Se requiere un titular personal.')
    resolve_company(user,provider.pk)
    if company.currency!='COP':raise AccountingError('Explicit COP books required; no implicit FX.')
    payroll = Planilla.objects.select_for_update().filter(pk=UUID(str(payroll_id)),perfil_id=provider.pk).first()
    if payroll is None:raise AccountingError('Payroll unavailable in selected company.')
    return user,company,payroll

def _policy(policy, payroll):
    if not isinstance(policy,dict) or not {'code','revision','valid_from','valid_until','divisor_days','components','evidence_digest'}<=set(policy) or set(policy)-{'code','revision','valid_from','valid_until','divisor_days','components','evidence_digest','earning_rules'}:
        raise AccountingError('Explicit bounded payroll policy required.')
    if not isinstance(policy['code'],str) or not re.fullmatch('[A-Z0-9][A-Z0-9_-]{0,39}',policy['code']) or type(policy['revision']) is not int or not 1<=policy['revision']<=10**9:
        raise AccountingError('Explicit policy identity/version required.')
    start=date.fromisoformat(policy['valid_from']);end=date.fromisoformat(policy['valid_until'])
    if start.isoformat()!=policy['valid_from'] or end.isoformat()!=policy['valid_until'] or not start<=payroll.periodo_inicio<=payroll.periodo_fin<=end or (end-start).days>3660:
        raise AccountingError('Policy must cover the whole payroll period.')
    if type(policy['divisor_days']) is not int or not 1<=policy['divisor_days']<=31:raise AccountingError('Explicit day divisor from1 to31 required.')
    _digest(policy['evidence_digest']);components=policy['components']
    if not isinstance(components,list) or not 1<=len(components)<=8:raise AccountingError('One to8 explicit policy components required.')
    supplemental='earning_rules' in policy
    if supplemental:
        from .declared_earnings import rules
        policy={**policy,'earning_rules':rules(policy['earning_rules'])}
    seen=set();normalized=[]
    for component in components:
        if not isinstance(component,dict) or set(component)!=({'code','kind','rate_bps','basis'} if supplemental else {'code','kind','rate_bps'}) or not isinstance(component['code'],str) or not re.fullmatch('[A-Z0-9][A-Z0-9_-]{0,29}',component['code']) or component['code'] in seen or component['kind'] not in KINDS or type(component['rate_bps']) is not int or not 0<=component['rate_bps']<=10000:
            raise AccountingError('Unique component with explicit kind and integer basis-point rate required.')
        if supplemental and component['basis'] not in {'BASE','GROSS'}:raise AccountingError('Explicit contribution basis BASE or GROSS required.')
        seen.add(component['code']);normalized.append(component)
    return {**policy,'components':sorted(normalized,key=lambda row:row['code'])}

def _accounts(company,mapping):
    if not isinstance(mapping,dict) or set(mapping)!=set(ACCOUNT_TYPES):raise AccountingError('All explicit expense/liability mappings required.')
    ids=[UUID(str(mapping[key])) for key in ACCOUNT_TYPES]
    if len(set(ids))!=len(ids):raise AccountingError('Use distinct mapped accounts; no inferred balancing accounts.')
    found={row.pk:row for row in Account.plain_objects.filter(tenant=company,pk__in=ids,is_active=True).select_related('chart_of_accounts')}
    result={}
    for key,identifier in zip(ACCOUNT_TYPES,ids):
        row=found.get(identifier)
        if row is None or row.type!=ACCOUNT_TYPES[key] or row.chart_of_accounts.tenant_id!=company.pk:raise AccountingError('Mapped account inactive, foreign or incompatible.')
        result[key]=row
    return result

def _calculation(company,payroll,policy,workers,mapping):
    policy=_policy(policy,payroll);_accounts(company,mapping)
    from apps.core_erp.accounting.opening_balances import inspect_opening
    inspect_opening(company.pk,cutoff=payroll.periodo_fin)
    if payroll.periodo_inicio>payroll.periodo_fin or payroll.periodo_fin>timezone.localdate() or (payroll.periodo_fin-payroll.periodo_inicio).days>31:
        raise AccountingError('Closed economic interval of at most32 calendar days required.')
    if not isinstance(workers,list) or not 1<=len(workers)<=10:raise AccountingError('This bounded accrual requires1 to10 employees.')
    if DetalleLiquidacion.objects.filter(planilla=payroll).exists():raise AccountingError('Legacy payroll details require separate reconciliation.')
    period=list(FiscalPeriod.plain_objects.filter(tenant=company,status='open',period_start__lte=payroll.periodo_inicio,period_end__gte=payroll.periodo_fin)[:2])
    if len(period)!=1:raise AccountingError('Exactly one open accounting period must cover payroll.')
    rows=[];seen=set();sums={key:0 for key in ['gross','net','deductions','employer','provisions']}
    for requested in sorted(workers,key=lambda row:str(row.get('employee_id','')) if isinstance(row,dict) else ''):
        if not isinstance(requested,dict) or set(requested)!=({'employee_id','contract_id','worked_days','earnings'} if 'earning_rules' in policy else {'employee_id','contract_id','worked_days'}) or type(requested['worked_days']) is not int or not 1<=requested['worked_days']<=min(policy['divisor_days'],(payroll.periodo_fin-payroll.periodo_inicio).days+1):
            raise AccountingError('Explicit employee/contract and positive worked days within divisor required.')
        employee_id=UUID(str(requested['employee_id']));contract_id=UUID(str(requested['contract_id']))
        if employee_id in seen:raise AccountingError('Employee repeated in payroll proposal.')
        seen.add(employee_id)
        employee=Empleado.objects.select_for_update().filter(pk=employee_id,perfil_id=payroll.perfil_id,estado='ACTIVO').first()
        contract=Contrato.objects.select_for_update().filter(pk=contract_id,empleado_id=employee_id,activo=True).first()
        if employee is None or contract is None or employee.framework_legal!='CO' or contract.tipo_contrato not in {'TERMINO_INDEFINIDO','TERMINO_FIJO'} or contract.fecha_inicio>payroll.periodo_inicio or (contract.fecha_fin and contract.fecha_fin<payroll.periodo_fin):
            raise AccountingError('Active scoped employee and contract covering the whole interval required.')
        if Contrato.objects.filter(empleado_id=employee_id,activo=True,fecha_inicio__lte=payroll.periodo_fin).filter(Q(fecha_fin__isnull=True)|Q(fecha_fin__gte=payroll.periodo_inicio)).exclude(pk=contract.pk).exists():
            raise AccountingError('Overlapping active contracts require separate review.')
        if DetalleLiquidacion.objects.filter(empleado=employee,planilla__periodo_inicio__lte=payroll.periodo_fin,planilla__periodo_fin__gte=payroll.periodo_inicio).exclude(planilla=payroll).exists():
            raise AccountingError('Overlapping payroll allocation requires reconciliation; do not accrue twice.')
        if Ausencia.objects.filter(empleado=employee,fecha_inicio__date__lte=payroll.periodo_fin,fecha_fin__date__gte=payroll.periodo_inicio).exists() or IncapacidadLaboral.objects.filter(empleado=employee,fecha_inicio__lte=payroll.periodo_fin,fecha_fin__gte=payroll.periodo_inicio).exists():
            raise AccountingError('Absence/incapacity requires a reviewed allocation; base-pay mode cannot ignore it.')
        if NovedadNomina.objects.filter(empleado=employee,planilla=payroll).exists() or NovedadNomina.objects.filter(empleado=employee,planilla__isnull=True).exists():
            raise AccountingError('Payroll with novelties requires reviewed allocation; base-pay mode cannot silently omit them.')
        # This route accrues base salary, not a supplemental/adjustment payroll.
        # Company lock serializes posting, so a second reviewed draft must recheck.
        if DetalleLiquidacion.objects.filter(empleado=employee,planilla__perfil_id=payroll.perfil_id,planilla__asiento_contable_ref_id__isnull=False,planilla__periodo_inicio__lte=payroll.periodo_fin,planilla__periodo_fin__gte=payroll.periodo_inicio).exclude(planilla=payroll).exists():
            raise AccountingError('An overlapping posted payroll already accrues this employee base salary; use a separately reviewed reconciliation/adjustment workflow.')
        salary=_money(format(contract.salario,'.2f'))
        if salary<=0:raise AccountingError('Positive exact contract salary required.')
        days=requested['worked_days'];divisor=policy['divisor_days'];base=(salary*days*2+divisor)//(2*divisor)
        if base<=0:raise AccountingError('Prorated base must be positive.')
        gross=base;earning_rows=[];earning_parts={}
        if 'earning_rules' in policy:
            from .declared_earnings import calculate
            earning_rows,earning_parts=calculate(requested['earnings'],policy['earning_rules'],salary,(payroll.periodo_fin-payroll.periodo_inicio).days+1,_digest)
            gross+=sum(earning_parts.values())
        components=[];parts={kind:0 for kind in KINDS}
        for rule in policy['components']:
            basis=gross if rule.get('basis')=='GROSS' else base
            cents=(basis*rule['rate_bps']+5000)//10000;parts[rule['kind']]+=cents
            components.append({**rule,**({'calculation_basis':rule['basis']} if 'basis' in rule else {}),'basis':_format_money(basis),'amount':_format_money(cents)})
        net=gross-parts['EMPLOYEE_DEDUCTION']
        if net<0:raise AccountingError('Deductions exceed declared base pay.')
        row={'employee_id':str(employee.pk),'contract_id':str(contract.pk),'worked_days':days,'contract_salary':_format_money(salary),
             'contract_start':contract.fecha_inicio.isoformat(),'contract_end':contract.fecha_fin.isoformat() if contract.fecha_fin else None,
             'cost_center':employee.centro_costo,'base':_format_money(base),'net':_format_money(net),'deductions':_format_money(parts['EMPLOYEE_DEDUCTION']),
             'employer':_format_money(parts['EMPLOYER_CONTRIBUTION']),'provisions':_format_money(parts['PROVISION']),'components':components}
        if 'earning_rules' in policy:row.update(gross=_format_money(gross),earnings=earning_rows,earning_totals={k:_format_money(v) for k,v in earning_parts.items()})
        rows.append(row)
        for key,value in [('gross',gross),('net',net),('deductions',parts['EMPLOYEE_DEDUCTION']),('employer',parts['EMPLOYER_CONTRIBUTION']),('provisions',parts['PROVISION'])]:sums[key]+=value
    totals={key:_format_money(value) for key,value in sums.items()}
    # Bound both the financial values and the canonical event size explicitly.
    for value in totals.values():_money(value)
    snapshot={'company_id':str(company.pk),'provider_id':str(payroll.perfil_id),'payroll_id':str(payroll.pk),
              'since':payroll.periodo_inicio.isoformat(),'until':payroll.periodo_fin.isoformat(),'period_id':str(period[0].pk),
              'policy':policy,'workers':rows,'totals':totals,'mapping':{k:str(UUID(str(v))) for k,v in mapping.items()},
              'currency':'COP','regulatory_verified':False,'schema':'sgacd-base-payroll-v1'}
    fingerprint(snapshot)
    return snapshot

def _latest(payroll):
    return OutboxEvent.objects.filter(event_type=REVIEW,aggregate_root=str(payroll.pk),payload__payroll_id=str(payroll.pk)).order_by('-payload__revision').first()

def _proof_id(payroll):return uuid5(NS,'applied:'+str(payroll.pk))
def _key(payroll):return 'payroll-accrual:'+str(payroll.pk)

@transaction.atomic
def review_payroll(*,actor,provider_id,payroll_id,policy,workers,account_mapping,evidence_digest,expected_revision,confirmed):
    user,company,payroll=_context(actor,provider_id,payroll_id)
    if confirmed is not True or type(expected_revision) is not int or expected_revision<0:raise AccountingError('First explicit payroll confirmation and revision required.')
    _digest(evidence_digest)
    if payroll.estado!='BORRADOR' or payroll.asiento_contable_ref_id or payroll.orden_pago_ref_id or OutboxEvent.objects.filter(pk=_proof_id(payroll)).exists():raise AccountingError('Only untouched payroll drafts may be reviewed.')
    snapshot=_calculation(company,payroll,policy,workers,account_mapping)
    old=_latest(payroll);revision=old.payload['revision'] if old else 0
    if expected_revision!=revision:raise AccountingError('Payroll review changed; reload.')
    terms=snapshot['policy'];policy_id=uuid5(NS,'policy:'+str(company.pk)+':'+terms['code']+':'+str(terms['revision']))
    policy_payload={'company_id':str(company.pk),'terms':terms,'digest':fingerprint(terms),'regulatory_verified':False}
    declared=OutboxEvent.objects.filter(pk=policy_id).first()
    if declared and (declared.event_type!=POLICY or declared.payload!=policy_payload):raise AccountingError('Payroll policy version conflicts with its existing declaration.')
    if not declared:OutboxEvent.objects.create(id=policy_id,event_type=POLICY,domain='accounting',aggregate_root=str(company.pk),payload=policy_payload,version=1)
    body={'snapshot':snapshot,'reviewed_by':str(user.pk),'evidence_digest':evidence_digest,'revision':revision+1}
    row=OutboxEvent.objects.create(id=uuid5(NS,'review:'+str(payroll.pk)+':'+str(revision+1)),event_type=REVIEW,domain='accounting',aggregate_root=str(payroll.pk),payload={'company_id':str(company.pk),'payroll_id':str(payroll.pk),'revision':revision+1,'review':body,'review_digest':fingerprint(body)},version=1)
    return {'company_id':str(company.pk),'review_id':str(row.pk),'preview':body,'ledger_written':False,'regulatory_verified':False}

def _verified_applied(company,payroll,review):
    proof=OutboxEvent.objects.filter(pk=_proof_id(payroll),event_type=APPLIED).first()
    if proof is None:return None
    p=proof.payload;body=review.payload['review'];snapshot=body['snapshot']
    if p.get('company_id')!=str(company.pk) or p.get('review_id')!=str(review.pk) or p.get('review_digest')!=fingerprint(body) or review.payload['review_digest']!=fingerprint(body):raise AccountingError('Payroll origin requires reconciliation.')
    journal=JournalEntry.plain_objects.filter(pk=p.get('journal_id'),tenant=company,is_posted=True,hash_version='v2').first()
    receipt=AccountingEventReceipt.objects.filter(tenant=company,event_id=_key(payroll)).first()
    totals=snapshot['totals']
    if journal is None or receipt is None or receipt.journal_id!=journal.pk or journal.compute_hash()!=p.get('journal_hash') or journal.system_hash!=p['journal_hash'] or payroll.estado!='CONTABILIZADA' or str(payroll.asiento_contable_ref_id)!=str(journal.pk) or payroll.orden_pago_ref_id or payroll.periodo_inicio.isoformat()!=snapshot['since'] or payroll.periodo_fin.isoformat()!=snapshot['until'] or any(format(getattr(payroll,field),'.2f')!=totals[key] for field,key in [('total_devengado','gross'),('total_deduccion','deductions'),('total_neto','net')]):raise AccountingError('Payroll header or posted origin changed.')
    if journal.financial_event_id!=_key(payroll) or journal.currency!='COP' or journal.base_currency!='COP' or journal.exchange_rate!=1 or str(journal.period_id)!=snapshot['period_id'] or journal.date.isoformat()!=snapshot['until']:
        raise AccountingError('Payroll journal scope or valuation changed.')
    expected=[]
    for key,side,value in [('salary_expense','debit',totals['gross']),('employee_payable','credit',totals['net']),('deductions_payable','credit',totals['deductions']),('employer_expense','debit',totals['employer']),('employer_payable','credit',totals['employer']),('provision_expense','debit',totals['provisions']),('provision_payable','credit',totals['provisions'])]:
        if _money(value)>0:expected.append((snapshot['mapping'][key],value if side=='debit' else '0.00',value if side=='credit' else '0.00'))
    actual=[(str(row.account_id),format(row.debit_amount,'.2f'),format(row.credit_amount,'.2f')) for row in LedgerEntry.plain_objects.filter(journal_entry=journal,tenant=company)]
    if sorted(expected)!=sorted(actual):raise AccountingError('Posted payroll lines do not match the reviewed totals.')
    details=list(DetalleLiquidacion.objects.filter(planilla=payroll).select_related('empleado').order_by('empleado_id'))
    expected_rows=sorted(snapshot['workers'],key=lambda row:row['employee_id'])
    if len(details)!=len(expected_rows):raise AccountingError('Payroll detail projection changed.')
    for detail,row in zip(details,expected_rows):
        if str(detail.empleado_id)!=row['employee_id'] or detail.empleado.perfil_id!=payroll.perfil_id or detail.dias_trabajados!=row['worked_days'] or any(format(getattr(detail,field),'.2f')!=row[key] for field,key in [('salario_base','contract_salary'),('basico','base'),('total_devengado','gross' if 'gross' in row else 'base'),('total_deduccion','deductions'),('otras_deducciones','deductions'),('total_neto','net')]):
            raise AccountingError('Payroll detail totals changed.')
        known={'salario_base','basico','total_devengado','total_deduccion','otras_deducciones','total_neto'}
        if 'earnings' in row:
            for field,value in row['earning_totals'].items():
                if format(getattr(detail,field),'.2f')!=value:raise AccountingError('Supplemental payroll detail changed.')
                known.add(field)
        if any(getattr(detail,field.name)!=0 for field in detail._meta.fields if field.get_internal_type()=='DecimalField' and field.name not in known):
            raise AccountingError('Unexpected statutory/detail amounts in a base-only projection.')

    policy=snapshot['policy'];identifier=uuid5(NS,'policy:'+str(company.pk)+':'+policy['code']+':'+str(policy['revision']))
    declared=OutboxEvent.objects.filter(pk=identifier,event_type=POLICY,payload__company_id=str(company.pk)).first()
    if declared is None or declared.payload.get('terms')!=policy or declared.payload.get('digest')!=fingerprint(policy):raise AccountingError('Payroll policy evidence missing or changed.')
    return {'company_id':str(company.pk),'journal_id':str(journal.pk),'payroll_id':str(payroll.pk),'ledger_written':True,'replayed':True,
            'reversed':JournalEntry.plain_objects.filter(tenant=company,is_posted=True,reversed_entry_id=journal.pk).exists(),
            'money_transferred':False,'regulatory_verified':False,'details_projection':'DECLARED_EARNINGS_TOTALS' if 'earning_rules' in snapshot['policy'] else 'BASE_TOTALS_ONLY'}

@transaction.atomic
def post_payroll(*,actor,provider_id,payroll_id,review_id,confirmed):
    user,company,payroll=_context(actor,provider_id,payroll_id)
    if confirmed is not True:raise AccountingError('Second explicit payroll confirmation required.')
    review=_latest(payroll)
    if review is None or review.pk!=UUID(str(review_id)):raise AccountingError('Current persisted payroll review required.')
    body=review.payload['review']
    if fingerprint(body)!=review.payload['review_digest'] or body['reviewed_by']!=str(user.pk):raise AccountingError('Review integrity or reviewing actor changed.')
    applied=_verified_applied(company,payroll,review)
    if applied:return applied
    if payroll.estado!='BORRADOR' or payroll.asiento_contable_ref_id or payroll.orden_pago_ref_id:raise AccountingError('Payroll no longer an untouched draft.')
    snapshot=body['snapshot'];workers=[{k:row[k] for k in ['employee_id','contract_id','worked_days']} for row in snapshot['workers']]
    if 'earning_rules' in snapshot['policy']:
        for requested,row in zip(workers,snapshot['workers']):requested['earnings']=[{k:e[k] for k in ('code','minutes','evidence_digest')} for e in row['earnings']]
    current=_calculation(company,payroll,snapshot['policy'],workers,snapshot['mapping'])
    if current!=snapshot:raise AccountingError('Payroll source changed after review.')
    policy_id=uuid5(NS,'policy:'+str(company.pk)+':'+snapshot['policy']['code']+':'+str(snapshot['policy']['revision']))
    declared=OutboxEvent.objects.filter(pk=policy_id,event_type=POLICY,payload__company_id=str(company.pk)).first()
    if declared is None or declared.payload.get('terms')!=snapshot['policy'] or declared.payload.get('digest')!=fingerprint(snapshot['policy']):raise AccountingError('Declared policy origin changed.')
    accounts=_accounts(company,snapshot['mapping']);totals=snapshot['totals'];lines=[]
    for key,side,value in [('salary_expense','debit',totals['gross']),('employee_payable','credit',totals['net']),('deductions_payable','credit',totals['deductions']),('employer_expense','debit',totals['employer']),('employer_payable','credit',totals['employer']),('provision_expense','debit',totals['provisions']),('provision_payable','credit',totals['provisions'])]:
        if _money(value)>0:lines.append({'account':accounts[key],side:value})
    journal=LedgerEngine.post_lines(tenant_id=company.pk,entry_date=payroll.periodo_fin,description='Reviewed declared payroll with supplements' if 'earning_rules' in snapshot['policy'] else 'Reviewed declared base-pay accrual',lines_data=lines,actor=user,idempotency_key=_key(payroll),period_id=snapshot['period_id'])
    for row in snapshot['workers']:
        DetalleLiquidacion.objects.create(planilla=payroll,empleado_id=row['employee_id'],salario_base=row['contract_salary'],dias_trabajados=row['worked_days'],basico=row['base'],total_devengado=row.get('gross',row['base']),**row.get('earning_totals',{}),total_deduccion=row['deductions'],otras_deducciones=row['deductions'],total_neto=row['net'])
    payroll.total_devengado=totals['gross'];payroll.total_deduccion=totals['deductions'];payroll.total_neto=totals['net'];payroll.asiento_contable_ref_id=journal.pk;payroll.estado='CONTABILIZADA'
    payroll.save(update_fields=['total_devengado','total_deduccion','total_neto','asiento_contable_ref_id','estado'])
    OutboxEvent.objects.create(id=_proof_id(payroll),event_type=APPLIED,domain='accounting',aggregate_root=str(payroll.pk),payload={'company_id':str(company.pk),'payroll_id':str(payroll.pk),'review_id':str(review.pk),'review_digest':fingerprint(body),'journal_id':str(journal.pk),'journal_hash':journal.system_hash},version=1)
    payroll.refresh_from_db()
    result=_verified_applied(company,payroll,review);result['replayed']=False
    return result

@transaction.atomic
def payroll_state(*,actor,provider_id,payroll_id):
    user,company,payroll=_context(actor,provider_id,payroll_id)
    review=_latest(payroll)
    if review and fingerprint(review.payload['review'])!=review.payload['review_digest']:raise AccountingError('Review evidence changed.')
    if review is None and OutboxEvent.objects.filter(pk=_proof_id(payroll)).exists():raise AccountingError('Payroll review origin missing.')
    applied=_verified_applied(company,payroll,review) if review else None
    if payroll.estado!='BORRADOR' and applied is None:raise AccountingError('Historical payroll requires reconciliation.')
    return {'company_id':str(company.pk),'payroll_id':str(payroll.pk),'read_only':True,
            'review_id':str(review.pk) if review else None,'preview':review.payload['review'] if review else None,
            'revision':review.payload['revision'] if review else 0,'applied':applied,
            'reviewed_by_current_owner':bool(review and review.payload['review']['reviewed_by']==str(user.pk)),
            'confirmations_restored':False,'regulatory_verified':False}

@transaction.atomic
def payroll_sources(*,actor,provider_id):
    """Bounded owner-only catalog; truncation is explicit, not a complete export."""
    user=current_actor(actor)
    if getattr(user,'is_agent',False):raise PermissionDenied('Se requiere un titular personal.')
    provider=TourismProvider.objects.select_for_update().filter(pk=UUID(str(provider_id)),owner_id=user.pk,is_active=True,status='ACTIVE').first()
    if provider is None:raise PermissionDenied('Empresa no autorizada.')
    company=resolve_company(user,provider.pk).tenant;company=lock_company(company.pk);resolve_company(current_actor(user),provider.pk)
    payrolls=list(Planilla.objects.filter(perfil_id=provider.pk).order_by('-periodo_fin','pk')[:21])
    contracts=list(Contrato.objects.filter(empleado__perfil_id=provider.pk,empleado__estado='ACTIVO',activo=True).select_related('empleado').order_by('pk')[:101])
    accounts=list(Account.plain_objects.filter(tenant=company,chart_of_accounts__tenant=company,is_active=True,type__in=['EXPENSE','LIABILITY']).order_by('code','pk')[:201])
    return {'company_id':str(company.pk),'read_only':True,
            'payrolls':[{'id':str(row.pk),'since':row.periodo_inicio.isoformat(),'until':row.periodo_fin.isoformat(),'state':row.estado} for row in payrolls[:20]],
            'contracts':[{'id':str(row.pk),'employee_id':str(row.empleado_id),'label':row.empleado.nombre+' '+row.empleado.apellido+' · '+row.cargo,'salary':format(row.salario,'.2f')} for row in contracts[:100]],
            'accounts':[{'id':str(row.pk),'code':row.code,'name':row.name,'type':row.type} for row in accounts[:200]],
            'truncated':len(payrolls)>20 or len(contracts)>100 or len(accounts)>200,
            'limits':{'payrolls':20,'contracts':100,'accounts':200},'regulatory_verified':False}
