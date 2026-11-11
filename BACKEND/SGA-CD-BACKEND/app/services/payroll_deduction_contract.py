"""Independently reconcile declared fixed deductions crossing the corporate bridge."""
import re

def cents(value):
    if not isinstance(value,str) or not re.fullmatch(r'(0|[1-9][0-9]{0,15})[.][0-9]{2}',value):raise ValueError('Exact COP deduction required.')
    return int(value.replace('.',''))

def validate(snapshot,requested=None):
    from .payroll_novelty_contract import validate as validate_novelties
    validate_novelties(snapshot,requested)
    policy=snapshot.get('policy',{})
    if 'fixed_deduction_rules' not in policy:
        if requested and 'fixed_deduction_rules' in requested.get('policy',{}):raise ValueError('Requested deductions missing from response.')
        return
    rules=policy['fixed_deduction_rules']
    if not isinstance(rules,list) or not 1<=len(rules)<=8 or any(not isinstance(r,dict) or set(r)!={'code','kind'} or r['kind']!='FIXED_EMPLOYEE_LIABILITY' or not isinstance(r['code'],str) or not re.fullmatch('[A-Z0-9][A-Z0-9_-]{0,29}',r['code']) for r in rules):raise ValueError('Explicit fixed deduction rules required.')
    known={r['code'] for r in rules}
    if len(known)!=len(rules):raise ValueError('Duplicate deduction rule.')
    workers=snapshot['workers'];totals={k:0 for k in ['gross','net','deductions','employer','provisions']};seen=set()
    if not isinstance(workers,list) or not 1<=len(workers)<=10:raise ValueError('Bounded payroll workers required.')
    inputs={w['employee_id']:w for w in requested['workers']} if requested else None
    if requested and (sorted(requested['policy'].get('fixed_deduction_rules',[]),key=lambda r:r['code'])!=rules or len(inputs)!=len(requested['workers'])):raise ValueError('Requested deduction rules changed.')
    for worker in workers:
        key=worker['employee_id'];values=worker.get('fixed_deductions');fixed=0;codes=set()
        if key in seen or not isinstance(values,list) or len(values)>8:raise ValueError('Unique bounded employee deductions required.')
        seen.add(key)
        for row in values:
            if not isinstance(row,dict) or set(row)!={'code','kind','amount','evidence_digest','authorization_digest','authorization_independently_verified'} or row['kind']!='FIXED_EMPLOYEE_LIABILITY' or row['code'] not in known or row['code'] in codes or row['authorization_independently_verified'] is not False:raise ValueError('Deduction identity or unverified authorization changed.')
            if any(not isinstance(row[k],str) or not re.fullmatch('[a-f0-9]{64}',row[k]) for k in ['evidence_digest','authorization_digest']):raise ValueError('Deduction support references required.')
            amount=cents(row['amount'])
            if amount<=0:raise ValueError('Positive deduction required.')
            codes.add(row['code']);fixed+=amount
        percentage=sum(cents(c['amount']) for c in worker['components'] if c['kind']=='EMPLOYEE_DEDUCTION');gross=cents(worker.get('gross',worker['base']));deductions=percentage+fixed
        if cents(worker['fixed_deductions_total'])!=fixed or cents(worker['percentage_deductions'])!=percentage or cents(worker['deductions'])!=deductions or cents(worker['net'])!=gross-deductions:raise ValueError('Payroll deductions or net do not reconcile.')
        if inputs is not None:
            original=inputs.get(key)
            if original is None or any(original[k]!=worker[k] for k in ['contract_id','worked_days']):raise ValueError('Requested worker changed.')
            actual=[{k:d[k] for k in ['code','amount','evidence_digest','authorization_digest']} for d in values]
            if actual!=sorted(original['fixed_deductions'],key=lambda d:d['code']):raise ValueError('Requested deduction changed.')
        for k in totals:totals[k]+=gross if k=='gross' else cents(worker[k])
    if inputs is not None and seen!=set(inputs):raise ValueError('Requested payroll employee omitted.')
    if any(cents(snapshot['totals'][k])!=v for k,v in totals.items()):raise ValueError('Payroll totals do not reconcile.')
