"""Bounded bulk reads for a register already holding the company transaction lock."""
from uuid import UUID,uuid5
from .models import JournalEntry,LedgerEntry,AccountingEventReceipt
from .exceptions import AccountingError
from .integrity import journal_hash,fingerprint
from . import commercial_tax_posting as commercial
from apps.core_erp.outbox_models import OutboxEvent

RESERVATION='accounting.reservation.recognized.v1'
RESERVATION_REVIEW='accounting.reservation.recognition-reviewed.v1'

def load(company,groups):
    identifiers=set(groups)
    for rows in groups.values():
        head=rows[0].journal_entry
        if head.is_reversal:
            if not head.reversed_entry_id:raise AccountingError('Reversal original is unavailable.')
            identifiers.add(head.reversed_entry_id)
    heads={r.pk:r for r in JournalEntry.plain_objects.filter(tenant=company,pk__in=identifiers,is_posted=True)}
    if set(heads)!=identifiers:raise AccountingError('Journal snapshot is incomplete.')
    lines={key:[] for key in heads}
    records=list(LedgerEntry.plain_objects.filter(tenant=company,journal_entry_id__in=identifiers).select_related('account').order_by('pk')[:20001])
    if len(records)>20000:raise AccountingError('Narrow the interval; at most20000 full journal lines are supported.')
    for line in records:lines[line.journal_entry_id].append(line)
    for head in heads.values():
        entries=lines[head.pk]
        if head.currency!='COP' or head.base_currency!='COP' or head.hash_version!='v2' or head.exchange_rate!=1 or journal_hash(head,entries,head.previous_hash or 'GENESIS_SARITA_2026')!=head.system_hash or any(l.tenant_id!=company.pk or l.account.tenant_id!=company.pk or l.currency!='COP' or l.amount_base!=l.debit_amount+l.credit_amount or l.amount_transaction!=l.debit_amount+l.credit_amount for l in entries):raise AccountingError('Journal currency or integrity requires reconciliation.')
    original_ids={str(head.reversed_entry_id if head.is_reversal else head.pk) for head in heads.values()}
    proofs=list(OutboxEvent.objects.filter(event_type=commercial.POSTED,payload__company_id=str(company.pk),payload__body__journal_id__in=original_ids)[:251])
    reservation_proofs=list(OutboxEvent.objects.filter(event_type=RESERVATION,payload__company_id=str(company.pk),payload__journal_id__in=original_ids)[:251])
    if len(proofs)>250 or len(reservation_proofs)>250:raise AccountingError('Conflicting origin proof count.')
    reviews_ids=[]
    for proof in proofs:
        body=commercial.checked(proof,commercial.POSTED,company.pk);reviews_ids.append(commercial.identifier(body['review_id']))
    reviews_ids.extend(proof.payload['review_id'] for proof in reservation_proofs)
    reviews={str(r.pk):r for r in OutboxEvent.objects.filter(pk__in=reviews_ids,payload__company_id=str(company.pk))}
    bodies={}
    for proof in proofs:
        p=proof.payload['body'];review=reviews.get(p['review_id']);body=commercial.checked(review,commercial.REVIEW,company.pk)
        if p['journal_id'] in bodies:raise AccountingError('Multiple commercial proofs for one journal.')
        bodies[p['journal_id']]=(proof,review,body)
    claims_ids={uuid5(commercial.NS,'document:'+str(company.pk)+':'+row[2]['fact']['document_digest']) for row in bodies.values()}
    claims={r.pk:r for r in OutboxEvent.objects.filter(pk__in=claims_ids)}
    keys=[commercial.event_key(company.pk,row[2]['document_id']) for row in bodies.values()]
    receipts={r.event_id:r for r in AccountingEventReceipt.objects.filter(tenant=company,event_id__in=keys)}
    commercial_bodies={}
    for identifier,(proof,review,body) in bodies.items():
        journal=heads.get(UUID(identifier));claim=claims.get(uuid5(commercial.NS,'document:'+str(company.pk)+':'+body['fact']['document_digest']))
        commercial.validate_posted_snapshot(company,review,body,proof,journal,receipts.get(commercial.event_key(company.pk,body['document_id'])),claim,lines.get(journal.pk,[]) if journal else [])
        commercial_bodies[identifier]=body
    for head in heads.values():
        if head.financial_event_id and head.financial_event_id.startswith('purchase-item-return:'):
            from apps.prestadores.mi_negocio.gestion_contable.compras.purchase_item_returns import register_body
            commercial_bodies[str(head.pk)]=register_body(company,head)
        if head.financial_event_id and head.financial_event_id.startswith('purchase-return:'):
            if len(head.financial_event_id.split(':'))==2:
                from apps.prestadores.mi_negocio.gestion_contable.compras.purchase_recovery import register_body
            else:
                from apps.prestadores.mi_negocio.gestion_contable.compras.purchase_returns import register_body
            commercial_bodies[str(head.pk)]=register_body(company,head)
    reservations={}
    for proof in reservation_proofs:
        p=proof.payload;review=reviews.get(p['review_id']);body=review.payload.get('review') if review else None
        if p['journal_id'] in reservations:raise AccountingError('Multiple reservation proofs for one journal.')
        if review is None or review.event_type!=RESERVATION_REVIEW or not isinstance(body,dict) or fingerprint(body)!=review.payload.get('review_digest') or review.payload.get('review_digest')!=p.get('review_digest') or body.get('company_id')!=str(company.pk):raise AccountingError('Reviewed reservation evidence changed.')
        original=heads.get(UUID(p['journal_id']))
        if original is None or original.is_reversal or original.system_hash!=p.get('journal_hash'):raise AccountingError('Reservation source journal evidence changed.')
        reservations[p['journal_id']]=(p,body)
    return heads,lines,commercial_bodies,reservations
