"""Validate analytical payroll-cost results without granting financial authority."""
import re
from uuid import UUID
from datetime import date

def identifier(value):
    if not isinstance(value,str) or str(UUID(value))!=value:raise ValueError('Canonical identifier required.')

def money(value):
    if not isinstance(value,str) or not re.fullmatch(r'[0-9]{1,16}\.[0-9]{2}',value):raise ValueError('Exact positive money string required.')
    return int(value.replace('.',''))

def false_flags(data,*names):
    if any(data.get(k) is not False for k in names):raise ValueError('Analytical action cannot claim financial authority.')

def preview(data,payroll,context):
    if data.get('schema')!='sgacd-payroll-operation-cost-v1' or data.get('company_id')!=context['tenant_id'] or data.get('provider_id')!=context['provider_id'] or data.get('payroll_id')!=payroll:raise ValueError('Preview scope mismatch.')
    false_flags(data,'source_independently_verified','statutory_payroll_rules_verified')
    identifier(data['journal_id']);identifier(data['payroll_review_id'])
    if not re.fullmatch('[0-9a-f]{64}',data.get('payroll_review_digest','')):raise ValueError('Missing source digest.')
    if data.get('timezone')!='America/Bogota' or data.get('allocation_basis')!='OWNER_DECLARED_PAID_CAPACITY_US' or data.get('rounding')!='LARGEST_REMAINDER_UUID_UNALLOCATED_LAST':raise ValueError('Unknown cost basis.')
    workers=data['capacities'];centers=data['operation_centers']
    if not isinstance(workers,list) or not 1<=len(workers)<=10 or not isinstance(centers,dict) or not 1<=len(centers)<=20:raise ValueError('Bounded capacity/center sources required.')
    ids=set()
    for row in workers:
        if set(row)!={'employee_id','capacity_seconds'}:raise ValueError('Unexpected capacity fields.')
        identifier(row['employee_id'])
        if row['employee_id'] in ids or type(row['capacity_seconds']) is not int or row['capacity_seconds']<=0:raise ValueError('Invalid capacity.')
        ids.add(row['employee_id'])
    for key,value in centers.items():
        identifier(key)
        if not isinstance(value,str) or not re.fullmatch('[A-Z0-9][A-Z0-9_.-]{0,39}',value):raise ValueError('Invalid center.')
    work=data['work_source']
    if not isinstance(work,list) or len(work)>100:raise ValueError('Bounded work provenance required.')
    for row in work:
        if set(row)!={'work_id','employee_id','operation_id','source_kind','started_at','ended_at','closure_id','duration_us','evidence_digest','recorded_by','closure_evidence_digest','closure_recorded_by'} or row['employee_id'] not in ids or row['source_kind'] not in ('MANUAL','DISPATCH') or type(row['duration_us']) is not int or row['duration_us']<=0:raise ValueError('Unexpected work provenance fields.')
        identifier(row['work_id'])
        if row['operation_id'] is not None and row['operation_id'] not in centers:raise ValueError('Unknown work operation.')
    totals={k:0 for k in ('salary','employer','provisions')};seen=set()
    for field in ('allocations','unallocated'):
        rows=data[field]
        if not isinstance(rows,list) or len(rows)>210:raise ValueError('Bounded cost rows required.')
        for row in rows:
            if set(row)!={'employee_id','operation_id','center_code','allocation_weight_us','amounts','total_cost'} or row['employee_id'] not in ids:raise ValueError('Cost row source mismatch.')
            key=(row['employee_id'],row['operation_id'])
            if key in seen:raise ValueError('Duplicate allocation.')
            seen.add(key)
            if field=='unallocated':
                if row['operation_id'] is not None or row['center_code'] is not None:raise ValueError('Unallocated cost was assigned.')
            elif row['operation_id'] not in centers or row['center_code']!=centers[row['operation_id']]:raise ValueError('Operation/center mismatch.')
            if type(row['allocation_weight_us']) is not int or row['allocation_weight_us']<0 or set(row['amounts'])!=set(totals):raise ValueError('Invalid cost weights/components.')
            amounts={k:money(v) for k,v in row['amounts'].items()}
            if sum(amounts.values())!=money(row['total_cost']):raise ValueError('Cost row does not reconcile.')
            for key,value in amounts.items():totals[key]+=value
    if set(data['posted_cost'])!=set(totals) or any(money(data['posted_cost'][k])!=v for k,v in totals.items()) or sum(totals.values())!=money(data['posted_total_cost']):raise ValueError('Allocation does not reconcile to posted payroll.')

def validate(operation,data,payload,context):
    if not isinstance(data,dict) or data.get('company_id')!=context['tenant_id']:raise ValueError('Foreign cost result.')
    false_flags(data,'ledger_written')
    if operation=='operation_labor_costs':
        if data.get('schema')!='sgacd-operation-labor-cost-v1' or data.get('provider_id')!=context['provider_id'] or data.get('operation_id')!=payload['order_id'] or data.get('since')!=payload['since'] or data.get('until')!=payload['until'] or data.get('read_only') is not True or data.get('currency')!='COP' or data.get('date_basis')!='PAYROLL_LEDGER_POSTING_DATE':raise ValueError('Report scope mismatch.')
        false_flags(data,'money_transferred','operational_cost_field_overwritten','other_costs_included','physical_execution_verified')
        if type(data.get('source_complete')) is not bool:raise ValueError('Coverage required.')
        known=money(data['known_current_cost']);lines=data['lines']
        if not isinstance(lines,list) or len(lines)>1000:raise ValueError('Bounded report required.')
        total=0;seen=set()
        for row in lines:
            if set(row)!={'allocation_id','payroll_id','journal_id','posting_date','revision','source_current','cost','centers'}:raise ValueError('Unexpected report fields.')
            for key in ('allocation_id','payroll_id','journal_id'):identifier(row[key])
            if row['payroll_id'] in seen or type(row['source_current']) is not bool or type(row['revision']) is not int or row['revision']<1:raise ValueError('Duplicate/invalid report source.')
            seen.add(row['payroll_id']);date.fromisoformat(row['posting_date'])
            amount=money(row['cost'])
            if row['source_current']:total+=amount
        if total!=known:raise ValueError('Report subtotal mismatch.')
        if data['source_complete']:
            if data['unqualified_allocations'] or data['unallocated_payrolls'] or any(not r['source_current'] for r in lines) or money(data['total_cost'])!=known:raise ValueError('False completeness.')
        elif data['total_cost'] is not None:raise ValueError('Incomplete report cannot claim total.')
        return
    payroll=payload['payroll_id'];identifier(payroll)
    if data.get('payroll_id')!=payroll:raise ValueError('Different payroll returned.')
    if operation=='payroll_cost_sources':
        if data.get('provider_id')!=context['provider_id'] or data.get('read_only') is not True or type(data.get('payroll_reversed')) is not bool:raise ValueError('Invalid sources.')
        false_flags(data,'clinical_content_returned','capacity_inferred');identifier(data['journal_id'])
        for key,limit in [('workers',10),('work',100),('operations',100)]:
            if not isinstance(data.get(key),list) or len(data[key])>limit:raise ValueError('Unbounded sources.')
        for row in data['workers']:
            if set(row)!={'employee_id','name','salary','employer','provisions','reviewed_payroll_center'}:raise ValueError('Unexpected employee fields.')
            identifier(row['employee_id'])
            for key in ('salary','employer','provisions'):money(row[key])
        for row in data['work']:
            if set(row)!={'work_id','employee_id','operation_id','started_at','ended_at','source_kind'}:raise ValueError('Unexpected work fields.')
            identifier(row['work_id']);identifier(row['employee_id'])
            if row['operation_id'] is not None:identifier(row['operation_id'])
        for row in data['operations']:
            if set(row)!={'operation_id','label','state'}:raise ValueError('Unexpected operation fields.')
            identifier(row['operation_id'])
        return
    false_flags(data,'money_transferred')
    if operation=='review_payroll_costs':
        identifier(data['review_id']);preview(data['preview'],payroll,context)
        if data.get('allocation_recorded') is not False or data.get('revision')!=payload['expected_revision']+1 or sorted(data['preview']['capacities'],key=lambda r:r['employee_id'])!=sorted(payload['capacities'],key=lambda r:r['employee_id']) or data['preview']['operation_centers']!=payload['operation_centers']:raise ValueError('Review does not match declared sources.')
    elif operation=='record_payroll_costs':
        identifier(data['allocation_id']);false_flags(data,'confirmations_restored')
        if data.get('allocation_recorded') is not True or type(data.get('source_current')) is not bool or type(data.get('replayed')) is not bool or type(data.get('revision')) is not int or data['revision']<1:raise ValueError('Invalid allocation state.')
    elif operation=='payroll_cost_state':
        false_flags(data,'confirmations_restored')
        if data.get('read_only') is not True:raise ValueError('Recovery must be read-only.')
        for field in ('review','recorded'):
            row=data[field]
            if row is not None:
                identifier(row['review_id' if field=='review' else 'allocation_id']);preview(row['preview'],payroll,context)
                if type(row.get('revision')) is not int or row['revision']<1:raise ValueError('Invalid revision.')
                if field=='recorded' and (type(row.get('source_current')) is not bool or row.get('effective_for_current_source') is not row['source_current']):raise ValueError('Invalid effective source state.')
    else:raise ValueError('Unknown cost operation.')
