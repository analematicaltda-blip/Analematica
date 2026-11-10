"""Validate bounded metadata and financial results from the native purchase adapter."""
import re
from uuid import UUID

def uuid(value):
    if not isinstance(value,str) or str(UUID(value))!=value:raise ValueError('Canonical identifier required.')

def positive(value):
    if type(value) is not int or not 1<=value<=9007199254740991:raise ValueError('Positive native identifier required.')

def validate(operation,data,payload,context):
    if not isinstance(data,dict) or data.get('company_id')!=context['tenant_id']:raise ValueError('Company result mismatch.')
    if operation=='native_purchase_history':
        if set(data)!={'company_id','provider_id','search','after_id','invoices','next_after_id','read_only','ledger_written','money_transferred','documents_returned','confirmations_restored','regulatory_verified'}:raise ValueError('Unexpected history envelope fields.')
        if data.get('provider_id')!=context['provider_id'] or data.get('search')!=payload['search'] or data.get('after_id')!=payload['after_id'] or data.get('read_only') is not True or any(data.get(k) is not False for k in ['ledger_written','money_transferred','documents_returned','confirmations_restored','regulatory_verified']):raise ValueError('Invalid history scope or permissions.')
        rows=data.get('invoices')
        if not isinstance(rows,list) or len(rows)>20:raise ValueError('Bounded history page required.')
        previous=payload['after_id'] or 0
        for row in rows:
            if set(row)!={'invoice_id','supplier_id','number','issue_date','subtotal','tax','gross','state','accounting_phase','source_changed','journal_id','review_revision'}:raise ValueError('Unexpected history fields.')
            positive(row['invoice_id']);positive(row['supplier_id'])
            if row['invoice_id']<=previous:raise ValueError('Ordered unique cursor required.')
            previous=row['invoice_id']
            if not isinstance(row['number'],str) or not row['number'].startswith(payload['search']) or not isinstance(row['state'],str):raise ValueError('History search mismatch.')
            from datetime import date
            if date.fromisoformat(row['issue_date']).isoformat()!=row['issue_date']:raise ValueError('Canonical date required.')
            for k in ['subtotal','tax','gross']:
                if not isinstance(row[k],str) or not re.fullmatch(r'[0-9]{1,16}[.][0-9]{2}',row[k]):raise ValueError('Exact history amounts required.')
            from decimal import Decimal
            if Decimal(row['subtotal'])+Decimal(row['tax'])!=Decimal(row['gross']):raise ValueError('History totals mismatch.')
            phase=row['accounting_phase'];revision=row['review_revision']
            if phase not in {'LEGACY_UNRECONCILED','CAPTURED','REVIEWED','POSTED','REVERSED'} or type(revision) is not int or revision<0:raise ValueError('Unknown accounting history phase.')
            if phase=='LEGACY_UNRECONCILED':
                if row['source_changed'] is not None or revision or row['journal_id'] is not None:raise ValueError('Legacy invoice cannot claim captured evidence.')
            else:
                if type(row['source_changed']) is not bool or (phase=='CAPTURED')!=(revision==0):raise ValueError('Invalid native review history.')
                if phase in {'POSTED','REVERSED'}:uuid(row['journal_id'])
                elif row['journal_id'] is not None:raise ValueError('Unposted invoice cannot claim journal.')
        cursor=data.get('next_after_id')
        if cursor is not None:positive(cursor)
        if cursor is not None and (len(rows)!=20 or cursor!=previous):raise ValueError('History cursor mismatch.')
        return
    if operation=='record_native_supplier':
        positive(data['supplier_id'])
        if data.get('ledger_written') is not False or data.get('identity_verified') is not False or type(data.get('replayed')) is not bool:raise ValueError('Supplier identity not independently verified.')
        return
    if operation=='native_supplier_sources':
        if data.get('provider_id')!=context['provider_id'] or data.get('read_only') is not True or data.get('ledger_written') is not False or data.get('documents_returned') is not False or data.get('identity_verified') is not False or not isinstance(data.get('suppliers'),list) or len(data['suppliers'])>20:raise ValueError('Invalid supplier source page.')
        if data.get('next_after_id') is not None:positive(data['next_after_id'])
        seen=set()
        for row in data['suppliers']:
            if set(row)!={'supplier_id','name','identification'} or not isinstance(row['name'],str) or not isinstance(row['identification'],str):raise ValueError('Unexpected supplier fields.')
            positive(row['supplier_id'])
            if row['supplier_id'] in seen:raise ValueError('Duplicate supplier.')
            seen.add(row['supplier_id'])
        return
    if operation=='native_purchase_sources':
        if data.get('provider_id')!=context['provider_id'] or data.get('read_only') is not True or data.get('ledger_written') is not False or data.get('documents_returned') is not False or not isinstance(data.get('invoices'),list) or len(data['invoices'])>20:raise ValueError('Invalid source page.')
        if data.get('next_after_id') is not None:positive(data['next_after_id'])
        seen=set()
        for row in data['invoices']:
            if set(row)!={'invoice_id','supplier_id','number','issue_date','subtotal','tax','gross','state'}:raise ValueError('Unexpected source fields.')
            positive(row['invoice_id']);positive(row['supplier_id'])
            if row['invoice_id'] in seen or not all(isinstance(row[k],str) and re.fullmatch(r'[0-9]{1,16}[.][0-9]{2}',row[k]) for k in ['subtotal','tax','gross']):raise ValueError('Invalid invoice source values.')
            seen.add(row['invoice_id'])
        return
    positive(data['invoice_id']);uuid(data['document_id'])
    if operation!='record_native_purchase' and data['invoice_id']!=payload['invoice_id']:raise ValueError('Different invoice returned.')
    if operation=='native_purchase_state':
        if data.get('read_only') is not True or data.get('confirmations_restored') is not False or data.get('native_source_verified') is not True or type(data.get('source_matches_review')) is not bool:raise ValueError('Recovery cannot restore confirmations.')
        if data.get('posted') is not None:
            posted=data['posted'];uuid(posted['journal_id'])
            if posted.get('company_id')!=context['tenant_id'] or posted.get('document_id')!=data['document_id'] or posted.get('ledger_written') is not True or any(posted.get(k) is not False for k in ['money_transferred','fiscal_document_created','regulatory_verified']):raise ValueError('Posted recovery context/status changed.')
        return
    if operation=='record_native_purchase':
        if data.get('ledger_written') is not False or data.get('fiscal_accepted') is not False or data.get('money_transferred') is not False or type(data.get('replayed')) is not bool:raise ValueError('Intake is not fiscal acceptance, accrual or payment.')
        return
    if data.get('native_source_verified') is not True or data.get('regulatory_verified') is not False or data.get('money_transferred') is not False:raise ValueError('Unverified native financial source.')
    posting=operation in {'post_native_purchase','reverse_native_purchase'}
    if data.get('ledger_written') is not posting:raise ValueError('Financial state mismatch.')
    uuid(data['journal_id'] if posting else data['review_id'])
    if posting and (data.get('fiscal_document_created') is not False or type(data.get('replayed')) is not bool):raise ValueError('Invalid posting result.')
