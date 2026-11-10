"""Explicit many-to-many cash associations; unmatched rows remain differences.

Whole ledger lines are reserved, including explicit partial allocations. Residual
amounts stay unresolved until release and a new combined review. A split may span
several statement rows in one batch; no banking operation is inferred.
"""
from uuid import UUID, uuid5
from django.db import transaction
from . import bank_reconciliation as bank
from .bank_statement import compare_statement
from .bank_resolutions import REASONS, coverage
from .invoice_intent import _money, _format_money
from .integrity import fingerprint
from .models import LedgerEntry
from .exceptions import AccountingError
from ..outbox_models import OutboxEvent

REVIEW='accounting.bank-groups.reviewed.v1'
APPLIED='accounting.bank-groups.confirmed.v1'


def checked(row, kind, company):
    if row is None or row.event_type != kind or row.domain != 'accounting' or row.version != 1:
        raise AccountingError('Grouped bank evidence unavailable.')
    body=row.payload.get('body')
    if not isinstance(body,dict) or body.get('company_id') != str(company.pk) or row.payload != {'body':body,'digest':fingerprint(body)}:
        raise AccountingError('Grouped bank evidence changed.')
    if kind==REVIEW and (row.pk!=uuid5(bank.NS,'group-review:'+fingerprint(body)) or row.aggregate_root!=body.get('statement_id')):raise AccountingError('Grouped review identity changed.')
    return body


def claims(proof, body):
    pairs=[]
    for line in body['lines']:
        pairs.append(('line:'+line['ledger_line_id'], line['ledger_line_id'], None))
    for row in body['rows']:
        pairs.append(('ref:'+row['transaction_ref_digest'], None, row['transaction_ref_digest']))
    return [(uuid5(bank.NS,'group-claim:'+str(proof.pk)+':'+key),
        {'company_id':body['company_id'],'account_id':body['account_id'],
        'reconciliation_id':str(proof.pk),'statement_id':body['statement_id'],
        'review_digest':fingerprint(body),'ledger_line_id':line,'transaction_ref_digest':ref}) for key,line,ref in pairs]


def origin(company, proof):
    posted=checked(proof,APPLIED,company)
    review=OutboxEvent.objects.filter(pk=posted['review_id']).first(); body=checked(review,REVIEW,company)
    if posted['review_digest'] != fingerprint(body) or proof.pk != uuid5(bank.NS,'group-applied:'+str(review.pk)):
        raise AccountingError('Grouped origin changed.')
    for identifier,payload in claims(proof,body):
        claim=OutboxEvent.objects.filter(pk=identifier,event_type=bank.CLAIM).first()
        if claim is None or claim.payload != payload: raise AccountingError('Grouped bank claim changed.')
    return body


def result(company, proof):
    body=origin(company,proof); released=bank._released(company,proof); valid=True
    try:bank._validate_rows(company,{**body,'rows':body['lines']},require_current_policy=False)
    except AccountingError:valid=False
    valid=valid and not released
    matched=[r for r in body['rows'] if r['row'] not in {d['row'] for d in body['differences']}]
    return {'company_id':str(company.pk),'reconciliation_id':str(proof.pk),'review_id':proof.payload['body']['review_id'],
        'coverage':coverage(matched,body['differences']),'groups':body['groups'],'differences':body['differences'],'ledger_remainders':body.get('ledger_remainders',[]),
        'associations_confirmed':valid,'fully_reconciled':valid and not body['differences'] and not body.get('ledger_remainders'),
        'released':released,'requires_review':not valid and not released,'bank_verified':False,'ledger_written':False,'money_transferred':False}


@transaction.atomic
def review_groups(company_id, *, actor, account_id, csv_text, groups, differences, evidence_digest, confirmed):
    company,user=bank._context(company_id,actor); bank.digest(evidence_digest)
    if confirmed is not True or not isinstance(groups,list) or not 1<=len(groups)<=30 or not isinstance(differences,list):
        raise AccountingError('First confirmation and explicit bounded groups required.')
    comparison=compare_statement(company.pk,account_id=account_id,csv_text=csv_text)
    if len(comparison['rows'])>30: raise AccountingError('At most thirty statement rows per group review.')
    account,policy=bank.cash_account(company,account_id)
    rows=[{k:r[k] for k in ['row','transaction_ref_digest','date','direction','amount']} for r in comparison['rows']]
    by_number={r['row']:r for r in rows}; used_rows=set(); used_lines=set(); lines=[]; normalized=[]; remainders=[]
    for group in groups:
        if not isinstance(group,dict) or set(group) not in ({'rows','ledger_line_ids'},{'rows','ledger_line_ids','ledger_allocations','remainder_reason'}) or not isinstance(group['rows'],list) or not group['rows'] or not isinstance(group['ledger_line_ids'],list) or not 1<=len(group['ledger_line_ids'])<=30:
            raise AccountingError('Exact nonempty statement/ledger group required.')
        selected=[]
        for number in group['rows']:
            if type(number) is not int or number not in by_number or number in used_rows:raise AccountingError('Statement rows may be allocated only once.')
            used_rows.add(number);selected.append(by_number[number])
        dates={r['date'] for r in selected}; directions={r['direction'] for r in selected}
        if len(dates)!=1 or len(directions)!=1:raise AccountingError('A group requires one explicit economic date and direction.')
        allocations=group.get('ledger_allocations')
        if allocations is not None and (not isinstance(allocations,dict) or set(allocations)!=set(group['ledger_line_ids']) or group['remainder_reason'] not in REASONS):
            raise AccountingError('Explicit allocation per ledger line and remainder reason required.')
        group_lines=[]; allocated_total=0
        for identifier in group['ledger_line_ids']:
            identifier=str(UUID(identifier))
            if identifier in used_lines:raise AccountingError('A ledger line may be allocated only once.')
            used_lines.add(identifier)
            line=LedgerEntry.plain_objects.filter(pk=identifier,tenant=company,account=account).select_related('journal_entry').first()
            if line is None:raise AccountingError('Scoped cash ledger line required.')
            journal=line.journal_entry
            group_lines.append({'ledger_line_id':identifier,'journal_id':str(journal.pk),'journal_hash':journal.system_hash,
                'date':next(iter(dates)),'direction':next(iter(directions)),
                'amount':format(line.debit_amount or line.credit_amount,'.2f')})
            full=_money(group_lines[-1]['amount']);allocated=_money(allocations[identifier]) if allocations is not None else full
            if not 0<allocated<=full:raise AccountingError('Partial allocation must be positive and cannot exceed the posted line.')
            allocated_total+=allocated
            if allocated<full:remainders.append({'ledger_line_id':identifier,'amount':_format_money(full-allocated),'direction':next(iter(directions)),'reason_code':group['remainder_reason']})
        if sum(_money(r['amount']) for r in selected)!=allocated_total:
            raise AccountingError('Grouped amounts must balance exactly; no rounding or implicit remainder.')
        lines.extend(group_lines);normalized.append({**group,'rows':sorted(group['rows']),'ledger_line_ids':sorted(group['ledger_line_ids'])})
    unresolved=[]
    for decision in differences:
        if not isinstance(decision,dict) or set(decision)!={'row','reason_code'} or type(decision['row']) is not int or decision['row'] not in by_number or decision['row'] in used_rows or decision['reason_code'] not in REASONS:
            raise AccountingError('Unique explicit unresolved bank row required.')
        used_rows.add(decision['row']);unresolved.append({**by_number[decision['row']],'reason_code':decision['reason_code']})
    if used_rows != set(by_number): raise AccountingError('Every bank row must be grouped or explicitly unresolved.')
    body={'company_id':str(company.pk),'statement_id':str(bank.statement_id(company.pk,account.pk,comparison['source_digest'])),
        'account_id':str(account.pk),'source_digest':comparison['source_digest'],'reviewed_by':str(user.pk),
        'policy_revision':policy['revision'],'policy_digest':policy['digest'],'evidence_digest':evidence_digest,
        'rows':rows,'lines':lines,'groups':normalized,'differences':unresolved,'ledger_remainders':remainders}
    bank._validate_rows(company,{**body,'rows':lines},require_current_policy=True)
    bank._conflicts(company,{**body,'rows':[dict(l,transaction_ref_digest=r['transaction_ref_digest']) for l in lines for r in rows], 'differences':[]})
    identifier=uuid5(bank.NS,'group-review:'+fingerprint(body))
    row,created=OutboxEvent.objects.get_or_create(pk=identifier,defaults={'event_type':REVIEW,'domain':'accounting','aggregate_root':body['statement_id'],'payload':{'body':body,'digest':fingerprint(body)},'version':1})
    checked(row,REVIEW,company)
    return {'company_id':str(company.pk),'review_id':str(identifier),'preview':body,'ledger_written':False,'bank_verified':False}


@transaction.atomic
def confirm_groups(company_id, *, actor, review_id, confirmed):
    company,user=bank._context(company_id,actor)
    review=OutboxEvent.objects.filter(pk=UUID(str(review_id))).first();body=checked(review,REVIEW,company)
    if confirmed is not True or body['reviewed_by']!=str(user.pk):raise AccountingError('Second confirmation by requesting owner required.')
    identifier=uuid5(bank.NS,'group-applied:'+str(review.pk));old=OutboxEvent.objects.filter(pk=identifier).first()
    if old:return {**result(company,old),'replayed':True}
    bank._validate_rows(company,{**body,'rows':body['lines']},require_current_policy=True)
    bank._conflicts(company,{**body,'rows':[dict(l,transaction_ref_digest=r['transaction_ref_digest']) for l in body['lines'] for r in body['rows']], 'differences':[]})
    value={'company_id':str(company.pk),'review_id':str(review.pk),'review_digest':fingerprint(body)}
    proof=OutboxEvent(id=identifier,event_type=APPLIED,payload={'body':value,'digest':fingerprint(value)})
    for key,payload in claims(proof,body):
        OutboxEvent.objects.create(id=key,event_type=bank.CLAIM,domain='accounting',aggregate_root=body['statement_id'],payload=payload,version=1)
    proof=OutboxEvent.objects.create(id=identifier,event_type=APPLIED,domain='accounting',aggregate_root=body['statement_id'],payload=proof.payload,version=1)
    return {**result(company,proof),'replayed':False}


@transaction.atomic
def group_state(company_id, *, actor, review_id):
    company,user=bank._context(company_id,actor)
    review=OutboxEvent.objects.filter(pk=UUID(str(review_id))).first();body=checked(review,REVIEW,company)
    proof=OutboxEvent.objects.filter(pk=uuid5(bank.NS,'group-applied:'+str(review.pk))).first()
    return {'company_id':str(company.pk),'review_id':str(review.pk),'preview':body,'applied':result(company,proof) if proof else None,
        'read_only':True,'confirmations_restored':False,'ledger_written':False,'bank_verified':False}


@transaction.atomic
def review_group_release(company_id, *, actor, review_id, reason_code, evidence_digest, confirmed):
    company,user=bank._context(company_id,actor);bank.digest(evidence_digest)
    review=OutboxEvent.objects.filter(pk=UUID(str(review_id))).first();checked(review,REVIEW,company)
    proof=OutboxEvent.objects.filter(pk=uuid5(bank.NS,'group-applied:'+str(review.pk))).first();body=origin(company,proof)
    if confirmed is not True or reason_code not in bank.REASONS or bank._released(company,proof):raise AccountingError('Explicit first review of an active grouped reconciliation required.')
    release={'company_id':str(company.pk),'statement_id':body['statement_id'],'reconciliation_id':str(proof.pk),
        'reviewed_by':str(user.pk),'reason_code':reason_code,'evidence_digest':evidence_digest,'origin_digest':fingerprint(proof.payload)}
    identifier=uuid5(bank.NS,'release-review:'+fingerprint(release))
    OutboxEvent.objects.get_or_create(pk=identifier,defaults={'event_type':bank.RELEASE_REVIEW,'domain':'accounting',
        'aggregate_root':body['statement_id'],'payload':{'company_id':str(company.pk),'review':release,'review_digest':fingerprint(release)},'version':1})
    return {'company_id':str(company.pk),'review_id':str(identifier),'ledger_written':False,'bank_verified':False}


@transaction.atomic
def confirm_group_release(company_id, *, actor, review_id, confirmed):
    company,user=bank._context(company_id,actor)
    row=OutboxEvent.objects.filter(pk=UUID(str(review_id)),event_type=bank.RELEASE_REVIEW,payload__company_id=str(company.pk)).first()
    release=row.payload.get('review') if row else None
    if confirmed is not True or not isinstance(release,dict) or release.get('reviewed_by')!=str(user.pk) or fingerprint(release)!=row.payload.get('review_digest'):
        raise AccountingError('Second explicit group release confirmation required.')
    proof=OutboxEvent.objects.filter(pk=release['reconciliation_id'],event_type=APPLIED).first();body=origin(company,proof)
    if release['origin_digest']!=fingerprint(proof.payload):raise AccountingError('Grouped origin changed before release.')
    identifier=uuid5(bank.NS,'released:'+str(proof.pk));payload={'company_id':str(company.pk),'reconciliation_id':str(proof.pk),'review_id':str(row.pk),'review_digest':fingerprint(release)}
    existing,created=OutboxEvent.objects.get_or_create(pk=identifier,defaults={'event_type':bank.RELEASED,'domain':'accounting','aggregate_root':body['statement_id'],'payload':payload,'version':1})
    if existing.payload!=payload:raise AccountingError('Another release already confirmed.')
    return {**result(company,proof),'replayed':not created}
