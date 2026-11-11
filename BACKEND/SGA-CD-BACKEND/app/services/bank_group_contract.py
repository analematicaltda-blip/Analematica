"""Validate exact group conservation and nonfinancial status at corporate boundary."""
import re,hashlib
from uuid import UUID

def uid(value):
    if not isinstance(value,str) or str(UUID(value))!=value:raise ValueError('Canonical identifier required.')

def money(value):
    if not isinstance(value,str) or not re.fullmatch(r'[0-9]{1,26}[.][0-9]{2}',value):raise ValueError('Exact nonnegative money required.')
    return int(value.replace('.',''))

def body(data,context):
    if data['company_id']!=context['tenant_id']:raise ValueError('Foreign review.')
    bank=data['bank_rows'];lines=data['ledger_lines'];groups=data['groups'];seen_bank=set();seen_lines=set();allocated={};partial='allocation_totals' in data
    if not isinstance(bank,list) or not 1<=len(bank)<=30 or not isinstance(lines,list) or not 1<=len(lines)<=60 or not isinstance(groups,list) or not 1<=len(groups)<=20:raise ValueError('Bounded group sources required.')
    bs={r['row']:r for r in bank};ls={r['ledger_line_id']:r for r in lines}
    if len(bs)!=len(bank) or len(ls)!=len(lines):raise ValueError('Duplicate sources.')
    for group in groups:
        uid(group['group_id']);b=group['bank_rows'];l=group['ledger_line_ids']
        if not b or not l or len(set(b))!=len(b) or len(set(l))!=len(l) or seen_bank.intersection(b) or not partial and seen_lines.intersection(l):raise ValueError('Reused group source.')
        bank_records=[bs[i] for i in b];records=bank_records+[ls[i] for i in l];day=bank_records[0]['date']
        if len({r['date'] for r in bank_records})!=1 or len({r['direction'] for r in records})!=1 or group['date']!=day or group['direction']!=records[0]['direction'] or sum(money(bs[i]['amount']) for i in b)!=money(group['amount']):raise ValueError('Group source does not conserve date/direction/amount.')
        if partial:
            entries=group['ledger_allocations']
            if len(entries)!=len(l) or {a['ledger_line_id'] for a in entries}!=set(l) or any(not data['ledger_since']<=ls[i]['date']<=day for i in l):raise ValueError('Allocated lines/date window mismatch.')
            if any(set(a)!={'ledger_line_id','amount'} or money(a['amount'])<=0 for a in entries) or sum(money(a['amount']) for a in entries)!=money(group['amount']):raise ValueError('Allocated amount differs from bank group.')
            for a in entries:allocated[a['ledger_line_id']]=allocated.get(a['ledger_line_id'],0)+money(a['amount'])
        elif len({r['date'] for r in records})!=1 or sum(money(ls[i]['amount']) for i in l)!=money(group['amount']):raise ValueError('Whole lines do not reconcile.')
        seen_bank.update(b);seen_lines.update(l)
    if seen_bank!=set(bs) or seen_lines!=set(ls):raise ValueError('Incomplete group source coverage.')
    if partial:
        if set(data['allocation_totals'])!=set(allocated) or any(money(data['allocation_totals'][key])!=value or value>money(ls[key]['available_amount']) for key,value in allocated.items()):raise ValueError('Allocated capacity does not reconcile.')

def validate(operation,data,payload,context):
    if not isinstance(data,dict) or data.get('company_id')!=context['tenant_id'] or any(data.get(k) is not False for k in ('ledger_written','money_transferred','bank_verified')):raise ValueError('Invalid group context/authority.')
    if operation=='bank_group_sources':
        if data.get('source_digest')!=hashlib.sha256(payload['csv_text'].encode()).hexdigest() or data.get('account_id')!=payload['account_id'] or data.get('read_only') is not True or data.get('raw_statement_stored') is not False or not isinstance(data.get('bank_rows'),list) or not 1<=len(data['bank_rows'])<=30 or not isinstance(data.get('ledger_lines'),list) or len(data['ledger_lines'])>200:raise ValueError('Invalid grouped sources.')
        for row in data['bank_rows']:
            if set(row)!={'row','transaction_ref_digest','date','direction','amount'} or type(row['row']) is not int or row['row']<1 or row['direction'] not in ('IN','OUT'):raise ValueError('Unexpected bank fields.')
            money(row['amount'])
        for row in data['ledger_lines']:
            if set(row)!={'ledger_line_id','journal_id','journal_hash','date','direction','amount','reserved_amount','available_amount'}:raise ValueError('Unexpected ledger fields.')
            uid(row['ledger_line_id']);uid(row['journal_id'])
            if money(row['reserved_amount'])+money(row['available_amount'])!=money(row['amount']):raise ValueError('Invalid remaining capacity.')
        return
    if operation=='review_bank_groups':
        uid(data['review_id']);uid(data['statement_id']);body(data['preview'],context)
        partial='allocation_totals' in data['preview']
        normalized=[{k:g[k] for k in ('group_id','bank_rows','ledger_allocations' if partial else 'ledger_line_ids')} for g in data['preview']['groups']]
        expected=[{**g,'bank_rows':sorted(g['bank_rows']),**({'ledger_allocations':sorted(g['ledger_allocations'],key=lambda a:a['ledger_line_id'])} if partial else {'ledger_line_ids':sorted(g['ledger_line_ids'])})} for g in payload['groups']]
        if payload.get('period') is not None and data['preview'].get('period_assessment',{}).get('terms')!=payload['period']:raise ValueError('Declared period changed.')
        if payload.get('period') is None and data['preview'].get('period_assessment') is not None:raise ValueError('Unrequested period assessment.')
        if payload.get('ledger_since') is not None and data['preview'].get('ledger_since')!=payload['ledger_since']:raise ValueError('Source window changed.')
        if sorted(normalized,key=lambda g:g['group_id'])!=sorted(expected,key=lambda g:g['group_id']) or data['preview']['source_digest']!=hashlib.sha256(payload['csv_text'].encode()).hexdigest() or data['preview']['account_id']!=payload['account_id'] or data['preview']['revision']!=payload['expected_revision']+1:raise ValueError('Returned groups differ from selection.')
        return
    if operation=='bank_group_state':
        if data.get('read_only') is not True or data.get('confirmations_restored') is not False or data.get('account_id')!=payload['account_id'] or data.get('source_digest')!=payload['source_digest']:raise ValueError('Invalid recovered group scope.')
        if data.get('preview') is not None:body(data['preview'],context)
        if data.get('applied') is not None:validate('confirm_bank_groups',data['applied'],{'statement_id':data['statement_id']},context)
        return
    uid(data['reconciliation_id']);uid(data['review_id'])
    if operation=='review_bank_group_release':
        if data['reconciliation_id']!=payload['reconciliation_id']:raise ValueError('Different grouped release origin.')
        return
    if data.get('schema')!='sgacd-bank-group-result-v1' or type(data.get('period_reconciled')) is not bool or data.get('confirmations_restored') is not False or any(type(data.get(k)) is not bool for k in ('groups_confirmed','requires_review','released','replayed')):raise ValueError('Invalid grouped financial state.')
    assessment=data.get('period_assessment');current=data.get('period_source_current')
    if assessment is None:
        if current is not None or data['period_reconciled']:raise ValueError('No period was assessed.')
    else:
        if type(current) is not bool or assessment.get('schema')!='sgacd-bank-period-assessment-v1' or assessment.get('source_independently_verified') is not False or type(assessment.get('eligible_for_period_reconciliation')) is not bool or type(assessment.get('group_allocations_complete')) is not bool:raise ValueError('Invalid period source.')
        if assessment['eligible_for_period_reconciliation'] and (assessment.get('balances_match') is not True or assessment.get('unmatched_ledger_line_ids')!=[] or assessment.get('unresolved_bank_rows')!=0 or not assessment['group_allocations_complete']):raise ValueError('Incomplete allocation cannot qualify a period.')
        if data['period_reconciled']!=(data['groups_confirmed'] and current and assessment['eligible_for_period_reconciliation']):raise ValueError('Stale or partial period cannot be qualified.')
    if data['groups_confirmed'] is not (not data['released'] and not data['requires_review']):raise ValueError('Stale/released group cannot remain confirmed.')
    if operation=='confirm_bank_groups' and data['statement_id']!=payload['statement_id']:raise ValueError('Different statement returned.')
    balances=data.get('line_balances')
    if data.get('allocation_totals') is not None and data['groups_confirmed'] and not isinstance(balances,list):raise ValueError('Partial confirmation needs capacity balances.')
    if balances is not None:
        if not isinstance(balances,list) or len(balances)!=data['ledger_line_count'] or len({r['ledger_line_id'] for r in balances})!=len(balances):raise ValueError('Invalid capacity list.')
        if data.get('allocation_totals') is not None and data['groups_confirmed'] and set(data['allocation_totals'])!={r['ledger_line_id'] for r in balances}:raise ValueError('Allocated balances refer to different lines.')
        for row in balances:
            uid(row['ledger_line_id'])
            if data.get('allocation_totals') is not None and data['groups_confirmed'] and money(row['reserved_amount'])<money(data['allocation_totals'][row['ledger_line_id']]):raise ValueError('Own active allocation is missing from reserved capacity.')
            if set(row)!={'ledger_line_id','amount','reserved_amount','available_amount'} or money(row['reserved_amount'])+money(row['available_amount'])!=money(row['amount']):raise ValueError('Capacity conservation failed.')
    for key,maximum in [('group_count',20),('bank_row_count',30),('ledger_line_count',60)]:
        if type(data.get(key)) is not int or not 1<=data[key]<=maximum:raise ValueError('Invalid group counts.')

