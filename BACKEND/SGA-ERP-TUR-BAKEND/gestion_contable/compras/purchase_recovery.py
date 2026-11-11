"""Append-only purchase audit: pre-post corrections and proportional returns."""
from datetime import date,timedelta
from uuid import UUID
from django.db import transaction
from django.utils import timezone
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.integrity import fingerprint
from apps.core_erp.accounting.models import JournalEntry, LedgerEntry, Account
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.outbox_models import OutboxEvent
from . import native_purchase as native

CORRECTION_REVIEW='accounting.native-purchase.correction-reviewed.v1'
CORRECTED='accounting.native-purchase.corrected.v1'
RETURN_REVIEW='accounting.native-purchase.return-reviewed.v1'
RETURNED='accounting.native-purchase.returned.v1'


def events(company,invoice_id,kind):
    rows=OutboxEvent.objects.filter(event_type=kind,aggregate_root=str(company.pk),payload__body__invoice_id=invoice_id).order_by('payload__body__revision')
    result=[]
    for row in rows[:101]:result.append((row,native.read_proof(row,kind,company.pk)))
    if len(result)>100:raise AccountingError('Reviewed extended purchase history required.')
    return result


def effective_capture(company,row,body):
    previous=body['captured_snapshot_digest']
    for revision,(event,change) in enumerate(events(company,row.pk,CORRECTED),1):
        if change['revision']!=revision or change['previous_digest']!=previous:raise AccountingError('Purchase correction chain changed.')
        review=native.read_proof(OutboxEvent.objects.filter(pk=change['review_id']).first(),CORRECTION_REVIEW,company.pk)
        if change['review_digest']!=fingerprint(review) or review['before_digest']!=previous or fingerprint(change['after_snapshot'])!=change['after_digest']:
            raise AccountingError('Purchase correction origin changed.')
        expected={**review['before_snapshot'],'subtotal':review['changes']['subtotal'],'tax':review['changes']['tax'],
            'gross':review['changes']['gross'],'due_date':review['changes']['due_date'],'notes_digest':fingerprint(review['changes']['notes'])}
        if fingerprint(review['before_snapshot'])!=previous or change.get('before_snapshot')!=review['before_snapshot'] or expected!=change['after_snapshot']:
            raise AccountingError('Purchase correction changed unrelated source fields.')
        previous=change['after_digest']
    return {**body,'captured_snapshot_digest':previous}


@transaction.atomic
def review_correction(*,actor,provider_id,invoice_id,request_id,changes,evidence_digest,confirmed):
    user,provider,company=native.context(actor,provider_id);row=native.invoice(provider,invoice_id)
    capture=native.capture_for(company,row);native.ledger.digest(evidence_digest)
    if confirmed is not True or not isinstance(changes,dict) or not changes or set(changes)-{'subtotal','tax','gross','due_date','notes'}:
        raise AccountingError('Explicit supported purchase corrections required.')
    if native.ledger.latest(company.pk,native.document(company,row)) or row.estado not in {'POR_PAGAR','VENCIDA'}:
        raise AccountingError('Only unreviewed unpaid purchases may change; posted sources require return/reversal.')
    if fingerprint(native.snapshot(row))!=capture['captured_snapshot_digest']:raise AccountingError('Untracked purchase source change.')
    amounts={k:changes.get(k,format(getattr(row,attr),'.2f')) for k,attr in [('subtotal','subtotal'),('tax','impuestos'),('gross','total')]}
    values={k:native._money(v) for k,v in amounts.items()}
    if values['subtotal']<=0 or values['subtotal']+values['tax']!=values['gross']:raise AccountingError('Exact net plus tax equals gross required.')
    due=changes.get('due_date',row.fecha_vencimiento.isoformat() if row.fecha_vencimiento else None)
    if due is not None and (date.fromisoformat(due).isoformat()!=due or due<row.issue_date.isoformat()):raise AccountingError('Invalid due date.')
    notes=changes.get('notes',row.notas)
    if not isinstance(notes,str) or len(notes)>2000:raise AccountingError('Bounded purchase notes required.')
    body={'company_id':str(company.pk),'invoice_id':row.pk,'request_id':request_id,'actor_id':str(user.pk),
        'before_snapshot':native.snapshot(row),'before_digest':fingerprint(native.snapshot(row)),'changes':{**amounts,'due_date':due,'notes':notes},
        'evidence_digest':evidence_digest,'expires_at':(timezone.now()+timedelta(minutes=15)).isoformat()}
    old=OutboxEvent.objects.filter(pk=native.proof_key(CORRECTION_REVIEW,company.pk,request_id)).first()
    if old:
        prior=native.read_proof(old,CORRECTION_REVIEW,company.pk)
        if any(prior[k]!=body[k] for k in body if k!='expires_at'):raise AccountingError('Correction key already used.')
        return {'review_id':str(old.pk),'ledger_written':False}
    saved=native.store(CORRECTION_REVIEW,company.pk,request_id,body)
    return {'review_id':str(saved.pk),'ledger_written':False}


@transaction.atomic
def confirm_correction(*,actor,provider_id,invoice_id,review_id,confirmed):
    user,provider,company=native.context(actor,provider_id);row=native.invoice(provider,invoice_id)
    proof=OutboxEvent.objects.filter(pk=UUID(str(review_id))).first();body=native.read_proof(proof,CORRECTION_REVIEW,company.pk)
    if confirmed is not True or body['invoice_id']!=row.pk or body['actor_id']!=str(user.pk):raise AccountingError('Second correction authorization required.')
    old=OutboxEvent.objects.filter(pk=native.proof_key(CORRECTED,company.pk,body['request_id'])).first()
    if old:
        native.capture_for(company,row)
        return {'correction_id':str(old.pk),'replayed':True,'ledger_written':False}
    if timezone.now()>=timezone.datetime.fromisoformat(body['expires_at']) or fingerprint(native.snapshot(row))!=body['before_digest'] or native.ledger.latest(company.pk,native.document(company,row)):
        raise AccountingError('Purchase changed, reviewed or correction expired.')
    for key,attr in [('subtotal','subtotal'),('tax','impuestos'),('gross','total'),('notes','notas')]:setattr(row,attr,body['changes'][key])
    row.fecha_vencimiento=date.fromisoformat(body['changes']['due_date']) if body['changes']['due_date'] else None
    row.save(update_fields=['subtotal','impuestos','total','notas','fecha_vencimiento']);row.refresh_from_db()
    snapshot=native.snapshot(row)
    saved=native.store(CORRECTED,company.pk,body['request_id'],{'company_id':str(company.pk),'invoice_id':row.pk,
        'request_id':body['request_id'],'revision':len(events(company,row.pk,CORRECTED))+1,'previous_digest':body['before_digest'],
        'before_snapshot':body['before_snapshot'],'after_snapshot':snapshot,'after_digest':fingerprint(snapshot),'review_id':str(proof.pk),'review_digest':fingerprint(body)})
    return {'correction_id':str(saved.pk),'replayed':False,'ledger_written':False}


def original(actor,provider_id,invoice_id):
    user,provider,company=native.context(actor,provider_id);row=native.invoice(provider,invoice_id)
    state=native.purchase_state(actor=user,provider_id=provider.pk,invoice_id=row.pk)
    if state['posted'] is None or state['posted']['reversed']:raise AccountingError('Unreversed posted native purchase required.')
    journal=JournalEntry.plain_objects.get(pk=state['posted']['journal_id'],tenant=company)
    return user,provider,company,row,journal


def returns(company,row):
    from .purchase_returns import POSTED
    if OutboxEvent.objects.filter(event_type=POSTED,payload__body__company_id=str(company.pk),payload__body__invoice_id=row.pk).exists():raise AccountingError('This invoice uses the native net-amount return protocol; reconcile it there before changing protocol.')
    results=[]
    for event,body in events(company,row.pk,RETURNED):
        review=native.read_proof(OutboxEvent.objects.filter(pk=body['review_id']).first(),RETURN_REVIEW,company.pk)
        journal=JournalEntry.plain_objects.filter(pk=body['journal_id'],tenant=company,is_posted=True).first()
        actual=sorted((str(l.account_id),format(l.debit_amount,'.2f'),format(l.credit_amount,'.2f')) for l in LedgerEntry.plain_objects.filter(journal_entry=journal,tenant=company))
        if journal is None or JournalEntry.plain_objects.filter(tenant=company,is_posted=True,reversed_entry_id=journal.pk).exists() or journal.compute_hash()!=body['journal_hash'] or journal.system_hash!=body['journal_hash'] or body['review_digest']!=fingerprint(review) or actual!=sorted((l['account'],l['debit'],l['credit']) for l in review['lines']):raise AccountingError('Purchase return evidence changed.')
        results.append(body)
    return results


@transaction.atomic
def review_return(*,actor,provider_id,invoice_id,request_id,return_bps,economic_date,reason_code,evidence_digest,confirmed):
    user,provider,company,row,journal=original(actor,provider_id,invoice_id);native.ledger.digest(evidence_digest)
    history=returns(company,row)
    if confirmed is not True or type(return_bps) is not int or not 1<=return_bps<=10000 or sum(r['return_bps'] for r in history)+return_bps>10000 or not isinstance(reason_code,str) or not native.re.fullmatch('[A-Z_]{1,40}',reason_code):raise AccountingError('Explicit bounded proportional return and reason required.')
    day=date.fromisoformat(economic_date)
    if day.isoformat()!=economic_date or not journal.date<=day<=timezone.localdate():raise AccountingError('Return date must follow original posting and not be future.')
    lines=[]
    for line in LedgerEntry.plain_objects.filter(journal_entry=journal,tenant=company):
        debit=native._money(format(line.credit_amount,'.2f'))*return_bps;credit=native._money(format(line.debit_amount,'.2f'))*return_bps
        if debit%10000 or credit%10000:raise AccountingError('Proportional return produces fractional cents; no silent rounding.')
        if debit or credit:lines.append({'account':str(line.account_id),'debit':native._format_money(debit//10000),'credit':native._format_money(credit//10000)})
    body={'company_id':str(company.pk),'invoice_id':row.pk,'request_id':request_id,'actor_id':str(user.pk),'original_journal_id':str(journal.pk),
        'original_hash':journal.system_hash,'return_bps':return_bps,'prior_returns_digest':fingerprint(history),'lines':lines,
        'economic_date':economic_date,'reason_code':reason_code,'evidence_digest':evidence_digest,'expires_at':(timezone.now()+timedelta(minutes=15)).isoformat()}
    old=OutboxEvent.objects.filter(pk=native.proof_key(RETURN_REVIEW,company.pk,request_id)).first()
    if old:
        prior=native.read_proof(old,RETURN_REVIEW,company.pk)
        if any(body[k]!=prior[k] for k in body if k!='expires_at'):raise AccountingError('Return key reused with other evidence.')
        return {'review_id':str(old.pk),'ledger_written':False}
    saved=native.store(RETURN_REVIEW,company.pk,request_id,body)
    return {'review_id':str(saved.pk),'preview':body,'ledger_written':False,'money_transferred':False}


@transaction.atomic
def confirm_return(*,actor,provider_id,invoice_id,review_id,confirmed):
    user,provider,company,row,journal=original(actor,provider_id,invoice_id)
    review=OutboxEvent.objects.filter(pk=UUID(str(review_id))).first();body=native.read_proof(review,RETURN_REVIEW,company.pk)
    if confirmed is not True or body['actor_id']!=str(user.pk) or body['invoice_id']!=row.pk:raise AccountingError('Second return authorization required.')
    history=returns(company,row)
    prior=next((r for r in history if r['review_id']==str(review.pk)),None)
    if prior:return {**prior,'replayed':True,'ledger_written':True,'money_transferred':False}
    if fingerprint(history)!=body['prior_returns_digest'] or journal.system_hash!=body['original_hash'] or str(journal.pk)!=body['original_journal_id'] or timezone.now()>=timezone.datetime.fromisoformat(body['expires_at']):raise AccountingError('Return history changed or review expired.')
    posted=LedgerEngine.post_lines(tenant_id=company.pk,actor=user,entry_date=date.fromisoformat(body['economic_date']),description='Reviewed native purchase return',
        idempotency_key='purchase-return:'+str(review.pk),lines_data=[{**l,'account':Account.plain_objects.get(pk=l['account'],tenant=company)} for l in body['lines']])
    value={'company_id':str(company.pk),'invoice_id':row.pk,'request_id':body['request_id'],'revision':len(history)+1,
        'review_id':str(review.pk),'review_digest':fingerprint(body),'return_bps':body['return_bps'],'journal_id':str(posted.pk),'journal_hash':posted.system_hash}
    native.store(RETURNED,company.pk,body['request_id'],value)
    return {**value,'replayed':False,'ledger_written':True,'money_transferred':False,'fiscal_document_created':False}


@transaction.atomic
def history(*,actor,provider_id,invoice_id):
    user,provider,company=native.context(actor,provider_id);row=native.invoice(provider,invoice_id);capture=native.capture_for(company,row)
    corrections=[body for _,body in events(company,row.pk,CORRECTED)]
    return {'invoice_id':row.pk,'capture':capture,'corrections':corrections,'returns':returns(company,row),
        'state':native.purchase_state(actor=user,provider_id=provider.pk,invoice_id=row.pk),'read_only':True,'confirmations_restored':False}


def register_body(company,journal):
    """Attribute exact contra components to the immutable original purchase.

    Revalidate proof chain, receipt and proportions. No fiscal acceptance, note
    issuance or bank settlement is inferred from this internal register view.
    """
    from types import SimpleNamespace
    from .purchase_returns import original as original_body
    from apps.core_erp.accounting.models import AccountingEventReceipt
    candidates=list(OutboxEvent.objects.filter(event_type=RETURNED,aggregate_root=str(company.pk),payload__body__company_id=str(company.pk),payload__body__journal_id=str(journal.pk))[:2])
    if len(candidates)!=1:raise AccountingError('Unique proportional return origin required.')
    posted=native.read_proof(candidates[0],RETURNED,company.pk)
    document_id=str(native.uuid5(native.NS,'invoice:'+str(company.pk)+':'+str(posted['invoice_id'])))
    source,state=original_body(company,document_id)
    source_journal=JournalEntry.plain_objects.get(pk=state['journal_id'],tenant=company,is_posted=True)
    history=returns(company,SimpleNamespace(pk=posted['invoice_id']))
    if state['reversed']:raise AccountingError('Proportional return source was reversed.')
    target=None
    for index,item in enumerate(history,1):
        review=native.read_proof(OutboxEvent.objects.filter(pk=item['review_id']).first(),RETURN_REVIEW,company.pk)
        bps=review['return_bps']
        if type(bps) is not int or not 1<=bps<=10000 or item['return_bps']!=bps or item['revision']!=index or review['invoice_id']!=posted['invoice_id'] or review['request_id']!=item['request_id'] or review['original_journal_id']!=state['journal_id'] or review['original_hash']!=source_journal.system_hash or review['prior_returns_digest']!=fingerprint(history[:index-1]):raise AccountingError('Proportional return chain or source changed.')
        mapped=[]
        for line in source['preview']['lines']:
            debit=native._money(line['credit'])*bps;credit=native._money(line['debit'])*bps
            if debit%10000 or credit%10000:raise AccountingError('Proportional register cannot silently round cents.')
            if debit or credit:mapped.append({'account_id':line['account_id'],'kind':line['kind'],'debit':native._format_money(debit//10000),'credit':native._format_money(credit//10000)})
        expected=sorted((x['account_id'],x['debit'],x['credit']) for x in mapped)
        if expected!=sorted((x['account'],x['debit'],x['credit']) for x in review['lines']):raise AccountingError('Return attribution differs from original tax components.')
        head=JournalEntry.plain_objects.filter(pk=item['journal_id'],tenant=company,is_posted=True).first()
        event_id='purchase-return:'+item['review_id']
        receipt=AccountingEventReceipt.objects.filter(tenant=company,event_id=event_id,journal=head).first() if head else None
        contract={'schema':'manual-journal-v2','tenant_id':str(company.pk),'actor_id':int(review['actor_id']),'date':review['economic_date'],'description':'Reviewed native purchase return','period_id':None,'lines':review['lines']}
        if head is None or head.financial_event_id!=event_id or head.created_by_id!=int(review['actor_id']) or head.date.isoformat()!=review['economic_date'] or receipt is None or receipt.payload_hash!=fingerprint(contract):raise AccountingError('Proportional return posting receipt changed.')
        if head.pk==journal.pk:target=mapped
    if sum(item['return_bps'] for item in history)>10000 or target is None:raise AccountingError('Return history exceeds original or lacks selected journal.')
    return {'document_id':source['document_id'],'preview':{'lines':target}}
