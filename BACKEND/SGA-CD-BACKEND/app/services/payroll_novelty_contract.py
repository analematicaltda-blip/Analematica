"""Verify source references, classifications, gross, contributions and net."""
import copy,hashlib,json,re
from .payroll_deduction_contract import cents

def validate(snapshot,requested=None):
    policy=snapshot.get('policy',{});mode=policy.get('novelty_mode')
    if mode is None:
        if requested and requested.get('policy',{}).get('novelty_mode') is not None:raise ValueError('Requested novelty source omitted.')
        return
    if mode not in {'FIXED_LIABILITY_FROM_SOURCE','COMPENSATION_FROM_SOURCE'} or 'fixed_deduction_rules' in policy:raise ValueError('Unsupported novelty source mode.')
    mixed=mode=='COMPENSATION_FROM_SOURCE';field='novelty_items' if mixed else 'novelty_deductions';classification={}
    if mixed:
        rules=policy['source_earning_rules']
        if not isinstance(rules,list) or not 1<=len(rules)<=8:raise ValueError('Bounded source classifications required.')
        for rule in rules:
            if set(rule)!={'concept_id','detail_field'} or type(rule['concept_id']) is not int or rule['concept_id']<1 or rule['concept_id'] in classification or rule['detail_field'] not in {'bonificaciones','comisiones'}:raise ValueError('Explicit unique earning concept classification required.')
            classification[rule['concept_id']]=rule['detail_field']
        if requested:
            normalized=copy.deepcopy(requested['policy'])
            for key,order in [('components','code'),('earning_rules','code'),('source_earning_rules','concept_id')]:
                if key in normalized:normalized[key]=sorted(normalized[key],key=lambda r:r[order])
            if normalized!=policy:raise ValueError('Requested compensation policy changed.')
    workers=snapshot['workers'];seen=set();sources=set();totals={k:0 for k in ['gross','net','deductions','employer','provisions']}
    if not isinstance(workers,list) or not 1<=len(workers)<=10:raise ValueError('Bounded workers required.')
    inputs={w['employee_id']:w for w in requested['workers']} if requested else None
    if requested and (requested['policy'].get('novelty_mode')!=mode or len(inputs)!=len(requested['workers'])):raise ValueError('Requested mode/worker changed.')
    for w in workers:
        if w['employee_id'] in seen:raise ValueError('Repeated employee.')
        seen.add(w['employee_id']);rows=w[field];fixed=0;earned={'bonificaciones':0,'comisiones':0}
        if not isinstance(rows,list) or len(rows)>8:raise ValueError('Bounded source novelties required.')
        actual=[]
        for d in rows:
            s=d['source'];identifier=d['novelty_id'];earning=mixed and s['concept_kind']=='DEVENGADO'
            if type(identifier) is not int or identifier<1 or identifier in sources or s['novelty_id']!=identifier or s['employee_id']!=w['employee_id'] or s['payroll_id'] not in [None,snapshot['payroll_id']] or s['concept_kind'] not in ({'DEDUCCION','DEVENGADO'} if mixed else {'DEDUCCION'}) or s['quantity']!='1.00' or not snapshot['since']<=s['date']<=snapshot['until'] or s['amount']!=d['amount'] or d['authorization_independently_verified'] is not False:raise ValueError('Source identity, classification, amount or scope changed.')
            for k in ['evidence_digest','authorization_digest','source_digest']:
                if not isinstance(d[k],str) or not re.fullmatch('[0-9a-f]{64}',d[k]):raise ValueError('Source evidence reference required.')
            digest=hashlib.sha256(json.dumps(s,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest();amount=cents(d['amount'])
            if digest!=d['source_digest'] or amount<=0:raise ValueError('Source hash or positive amount changed.')
            if earning:
                target=classification.get(s['concept_id'])
                if target is None or d.get('earning_field')!=target:raise ValueError('Earning source classification changed.')
                earned[target]+=amount
            else:
                if 'earning_field' in d:raise ValueError('Deduction cannot be projected as earning.')
                fixed+=amount
            sources.add(identifier);actual.append({k:d[k] for k in ['novelty_id','evidence_digest','authorization_digest']})
        gross=cents(w.get('gross',w['base']));percentage=sum(cents(c['amount']) for c in w['components'] if c['kind']=='EMPLOYEE_DEDUCTION')
        if mixed:
            if set(w['source_earning_totals'])!=set(earned) or any(cents(w['source_earning_totals'][k])!=v for k,v in earned.items()) or cents(w['novelty_earnings_total'])!=sum(earned.values()) or gross!=cents(w['base'])+sum(cents(v) for v in w.get('earning_totals',{}).values())+sum(earned.values()):raise ValueError('Source earning projection/gross changed.')
            components={c['code']:c for c in w['components']};amounts={'EMPLOYEE_DEDUCTION':0,'EMPLOYER_CONTRIBUTION':0,'PROVISION':0}
            if len(components)!=len(w['components']) or set(components)!={r['code'] for r in policy['components']}:raise ValueError('Contribution components changed.')
            for rule in policy['components']:
                basis=cents(w['base']) if rule['basis']=='BASE' else gross;rate=rule['rate_bps'];c=components[rule['code']]
                if rule['basis'] not in {'BASE','GROSS'} or type(rate) is not int or not 0<=rate<=10000 or c['kind']!=rule['kind'] or c['rate_bps']!=rate or c['calculation_basis']!=rule['basis'] or cents(c['basis'])!=basis or cents(c['amount'])!=(basis*rate+5000)//10000:raise ValueError('Declared contribution basis or amount changed.')
                amounts[rule['kind']]+=cents(c['amount'])
            if cents(w['employer'])!=amounts['EMPLOYER_CONTRIBUTION'] or cents(w['provisions'])!=amounts['PROVISION']:raise ValueError('Employer/provision totals changed.')
        if cents(w['novelty_deductions_total'])!=fixed or cents(w['percentage_deductions'])!=percentage or cents(w['deductions'])!=fixed+percentage or cents(w['net'])!=gross-fixed-percentage:raise ValueError('Novelty deduction/net does not reconcile.')
        if inputs is not None:
            original=inputs.get(w['employee_id'])
            if original is None or any(original[k]!=w[k] for k in ['contract_id','worked_days']) or sorted(original[field],key=lambda r:r['novelty_id'])!=actual:raise ValueError('Requested source selection changed.')
        for k in totals:totals[k]+=gross if k=='gross' else cents(w[k])
    if inputs is not None and seen!=set(inputs):raise ValueError('Requested worker omitted.')
    if any(cents(snapshot['totals'][k])!=v for k,v in totals.items()):raise ValueError('Payroll totals changed.')
