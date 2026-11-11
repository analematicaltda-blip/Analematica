"""Owner-scoped native supplier/invoice intake and reviewed canonical accrual.
No legacy payment activation, invoice issuance or verification of supplier identity.
"""
from datetime import date
from uuid import UUID,uuid5
import re
from django.db import transaction
from django.utils import timezone
from apps.turismo.models import TourismProvider
from apps.turismo.services.company_identity import resolve_company
from apps.core_erp.accounting.validation import current_actor,lock_company
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.integrity import fingerprint
from apps.core_erp.accounting.invoice_intent import _money,_format_money
from apps.core_erp.accounting import commercial_tax_posting as ledger,source_bindings
from apps.core_erp.outbox_models import OutboxEvent
from rest_framework.exceptions import PermissionDenied
from .models import Proveedor,FacturaCompra

NS=UUID('605b91a8-c24a-4108-acd6-35f097862711')
SUPPLIER='accounting.native-purchase.supplier-recorded.v1'
INTAKE='accounting.native-purchase.invoice-recorded.v1'
POSTED='accounting.native-purchase.posted.v1'

def context(actor,provider_id):
    user=current_actor(actor)
    if getattr(user,'is_agent',False):raise PermissionDenied('Titular personal requerido.')
    provider=TourismProvider.objects.filter(pk=UUID(str(provider_id)),owner_id=user.pk,is_active=True,status='ACTIVE').first()
    if provider is None:raise PermissionDenied('Empresa propia vigente requerida.')
    company=lock_company(resolve_company(user,provider.pk).tenant.pk)
    provider=TourismProvider.objects.select_for_update().filter(pk=provider.pk,owner_id=user.pk,is_active=True,status='ACTIVE').first()
    if provider is None or resolve_company(user,provider.pk).tenant.pk!=company.pk or company.currency!='COP':raise PermissionDenied('Empresa contable incompatible.')
    return user,provider,company

def positive(value):
    if type(value) is not int or not 1<=value<=9007199254740991:raise AccountingError('Identificador nativo entero positivo requerido.')
    return value

def proof_key(kind,company,request):return uuid5(NS,kind+':'+str(company)+':'+ledger.identifier(request))

def read_proof(row,kind,company):
    if row is None or row.event_type!=kind or row.domain!='accounting' or row.version!=1 or set(row.payload)!={'body','digest'}:raise AccountingError('Native capture proof missing or incompatible.')
    body=row.payload['body']
    if not isinstance(body,dict) or body.get('company_id')!=str(company) or row.aggregate_root!=str(company) or fingerprint(body)!=row.payload['digest'] or row.pk!=proof_key(kind,company,body['request_id']):raise AccountingError('Native capture proof changed.')
    return body

def store(kind,company,request,body):
    return OutboxEvent.objects.create(id=proof_key(kind,company,request),event_type=kind,domain='accounting',aggregate_root=str(company),payload={'body':body,'digest':fingerprint(body)},version=1)

def supplier(provider,identifier):
    row=Proveedor.objects.select_for_update().filter(pk=positive(identifier),perfil_id=provider.pk).first()
    if row is None:raise AccountingError('Proveedor no disponible en esta empresa.')
    return row

def invoice(provider,identifier):
    row=FacturaCompra.objects.select_for_update().select_related('proveedor').filter(pk=positive(identifier),perfil_id=provider.pk).first()
    if row is None or row.proveedor.perfil_id!=provider.pk:raise AccountingError('Factura y proveedor deben pertenecer a la misma empresa.')
    return row

def document(company,row):return str(uuid5(NS,'invoice:'+str(company.pk)+':'+str(row.pk)))

def snapshot(row):
    return {'invoice_id':row.pk,'provider_id':str(row.perfil_id),'supplier_id':row.proveedor_id,'supplier_digest':fingerprint({'name':row.proveedor.nombre,'identification':row.proveedor.identificacion}),
        'number':row.number,'issue_date':row.issue_date.isoformat(),'due_date':row.fecha_vencimiento.isoformat() if row.fecha_vencimiento else None,'subtotal':format(row.subtotal,'.2f'),'tax':format(row.impuestos,'.2f'),'gross':format(row.total,'.2f'),'state':row.estado,'created_by':str(row.creado_por_id),'created_at':row.creado_en.isoformat(),'notes_digest':fingerprint(row.notas)}

def capture_for(company,row):
    key=uuid5(NS,'invoice-capture:'+str(company.pk)+':'+str(row.pk));link=OutboxEvent.objects.filter(pk=key).first()
    if link is None or link.event_type!='accounting.native-purchase.capture-link.v1' or link.domain!='accounting' or link.version!=1 or link.aggregate_root!=str(company.pk) or set(link.payload)!={'capture_id','invoice_id','company_id'} or link.payload.get('invoice_id')!=row.pk or link.payload.get('company_id')!=str(company.pk):raise AccountingError('Historical invoice requires reviewed reconciliation; do not invent native intake evidence.')
    capture=OutboxEvent.objects.filter(pk=link.payload['capture_id']).first();body=read_proof(capture,INTAKE,company.pk)
    if body['invoice_id']!=row.pk or body['provider_id']!=str(row.perfil_id):raise AccountingError('Native invoice/capture mismatch.')
    from .purchase_recovery import effective_capture
    return effective_capture(company,row,body)

@transaction.atomic
def record_supplier(*,actor,provider_id,request_id,name,identification,evidence_digest,confirmed):
    user,provider,company=context(actor,provider_id);ledger.digest(evidence_digest);ledger.identifier(request_id)
    if confirmed is not True or not isinstance(name,str) or name!=name.strip() or not 1<=len(name)<=255 or any(ord(c)<32 for c in name) or not isinstance(identification,str) or not re.fullmatch('[A-Z0-9-]{3,20}',identification):raise AccountingError('Explicit canonical supplier metadata required; no registry verification inferred.')
    data={'name':name,'identification':identification,'evidence_digest':evidence_digest};old=OutboxEvent.objects.filter(pk=proof_key(SUPPLIER,company.pk,request_id)).first()
    if old:
        p=read_proof(old,SUPPLIER,company.pk)
        if p['data_digest']!=fingerprint(data) or p['actor_id']!=str(user.pk):raise AccountingError('Request already bound to other supplier metadata.')
        row=supplier(provider,p['supplier_id'])
        if row.nombre!=name or row.identificacion!=identification:raise AccountingError('Supplier source changed; intake replay cannot overwrite or conceal it.')
        return {'company_id':str(company.pk),'supplier_id':p['supplier_id'],'replayed':True,'ledger_written':False,'identity_verified':False}
    if Proveedor.objects.filter(perfil_id=provider.pk,identificacion=identification).exists():raise AccountingError('Supplier identity already registered; select the existing supplier.')
    row=Proveedor.objects.create(perfil_id=provider.pk,nombre=name,identificacion=identification)
    positive(row.pk)
    store(SUPPLIER,company.pk,request_id,{'company_id':str(company.pk),'provider_id':str(provider.pk),'actor_id':str(user.pk),'request_id':request_id,'supplier_id':row.pk,'data_digest':fingerprint(data)})
    return {'company_id':str(company.pk),'supplier_id':row.pk,'replayed':False,'ledger_written':False,'identity_verified':False}

@transaction.atomic
def record_invoice(*,actor,provider_id,request_id,supplier_id,number,issue_date,due_date,subtotal,tax,gross,document_digest,evidence_digest,confirmed):
    user,provider,company=context(actor,provider_id);party=supplier(provider,supplier_id);ledger.identifier(request_id);ledger.digest(document_digest);ledger.digest(evidence_digest)
    issued=date.fromisoformat(issue_date);due=date.fromisoformat(due_date) if due_date is not None else None
    amounts=[_money(v) for v in [subtotal,tax,gross]]
    if confirmed is not True or not isinstance(number,str) or not re.fullmatch('[A-Z0-9][A-Z0-9/_-]{0,49}',number) or issued.isoformat()!=issue_date or issued>timezone.localdate() or due is not None and (due.isoformat()!=due_date or due<issued) or amounts[0]<=0 or amounts[0]+amounts[1]!=amounts[2]:raise AccountingError('Canonical purchase number/date and exact positive net+tax=gross required.')
    data={'supplier_id':supplier_id,'number':number,'issue_date':issue_date,'due_date':due_date,'subtotal':subtotal,'tax':tax,'gross':gross,'document_digest':document_digest,'evidence_digest':evidence_digest};old=OutboxEvent.objects.filter(pk=proof_key(INTAKE,company.pk,request_id)).first()
    if old:
        p=read_proof(old,INTAKE,company.pk)
        if p['data_digest']!=fingerprint(data) or p['actor_id']!=str(user.pk):raise AccountingError('Request already bound to other invoice metadata.')
        row=invoice(provider,p['invoice_id'])
        if fingerprint(snapshot(row))!=p['captured_snapshot_digest']:raise AccountingError('Invoice intake source changed; recover its current state instead.')
        return {'company_id':str(company.pk),'invoice_id':row.pk,'document_id':document(company,row),'replayed':True,'ledger_written':False,'fiscal_accepted':False,'money_transferred':False}
    if FacturaCompra.objects.filter(perfil_id=provider.pk,proveedor=party,number=number).exists() or OutboxEvent.objects.filter(pk=source_bindings.digest_id(company.pk,document_digest)).exists() or OutboxEvent.objects.filter(pk=uuid5(ledger.NS,'document:'+str(company.pk)+':'+document_digest)).exists():raise AccountingError('Invoice number or document digest already registered; reconcile existing source.')
    row=FacturaCompra.objects.create(perfil_id=provider.pk,proveedor=party,number=number,issue_date=issued,fecha_vencimiento=due,subtotal=subtotal,impuestos=tax,total=gross,estado='POR_PAGAR',creado_por=user)
    positive(row.pk);row.refresh_from_db()
    saved=store(INTAKE,company.pk,request_id,{'company_id':str(company.pk),'provider_id':str(provider.pk),'actor_id':str(user.pk),'request_id':request_id,'invoice_id':row.pk,'data_digest':fingerprint(data),'document_digest':document_digest,'captured_snapshot_digest':fingerprint(snapshot(row))})
    OutboxEvent.objects.create(id=uuid5(NS,'invoice-capture:'+str(company.pk)+':'+str(row.pk)),event_type='accounting.native-purchase.capture-link.v1',domain='accounting',aggregate_root=str(company.pk),payload={'capture_id':str(saved.pk),'invoice_id':row.pk,'company_id':str(company.pk)},version=1)
    source_bindings.reserve(company.pk,document(company,row),{'kind':'ERP_PURCHASE','provider_id':str(provider.pk),'invoice_id':row.pk},document_digest)
    return {'company_id':str(company.pk),'invoice_id':row.pk,'document_id':document(company,row),'replayed':False,'ledger_written':False,'fiscal_accepted':False,'money_transferred':False}

def source_binding(provider,row):return {'identity':{'kind':'ERP_PURCHASE','provider_id':str(provider.pk),'invoice_id':row.pk},'snapshot_digest':fingerprint(snapshot(row))}

def review_inputs(body):
    """Authorized metadata for rebuilding the exact persisted concept form."""
    from copy import deepcopy
    if body is None:return None
    return {'selection':deepcopy(body['fact']['items']),
            'settlement_account_id':body['fact']['settlement_account_id'],
            'revision':body['revision']}

@transaction.atomic
def review_purchase(*,actor,provider_id,invoice_id,selection,settlement_account_id,economic_fact,evidence_digest,expected_revision,confirmed):
    user,provider,company=context(actor,provider_id);row=invoice(provider,invoice_id);capture=capture_for(company,row)
    if economic_fact!='GOODS_OR_SERVICES_RECEIVED' or confirmed is not True or row.estado not in {'POR_PAGAR','VENCIDA'}:raise AccountingError('Explicit receipt of goods/services and an unpaid, uncancelled invoice required.')
    binding=source_binding(provider,row)
    if capture['captured_snapshot_digest']!=binding['snapshot_digest']:raise AccountingError('Native intake source changed; reconcile it instead of silently replacing the invoice.')
    fact={'document_id':document(company,row),'document_digest':capture['document_digest'],'counterparty_id':str(uuid5(NS,'supplier:'+str(provider.pk)+':'+str(row.proveedor_id))),'direction':'PURCHASE','entry_date':row.issue_date.isoformat(),'items':selection,'settlement_account_id':settlement_account_id}
    p=ledger.preview(company,fact)
    if p['totals']['net']!=format(row.subtotal,'.2f') or p['totals']['tax']!=format(row.impuestos,'.2f') or p['totals']['gross']!=format(row.total,'.2f'):raise AccountingError('Policy breakdown does not match the stored invoice amounts.')
    with source_bindings._permit(company.pk,fact['document_id'],binding,user.pk,'REVIEW'):
        result=ledger.review_fact(company.pk,actor=user,fact=fact,evidence_digest=evidence_digest,expected_revision=expected_revision,confirmed=confirmed,source_binding=binding)
    return {**result,'invoice_id':row.pk,'document_id':fact['document_id'],'native_source_verified':True,'economic_fact_independently_verified':False,'review_inputs':review_inputs(ledger.checked(ledger.latest(company.pk,fact['document_id']),ledger.REVIEW,company.pk))}

@transaction.atomic
def post_purchase(*,actor,provider_id,invoice_id,review_id,confirmed):
    user,provider,company=context(actor,provider_id);row=invoice(provider,invoice_id);capture_for(company,row);doc=document(company,row)
    review=ledger.latest(company.pk,doc);body=ledger.checked(review,ledger.REVIEW,company.pk);binding=body.get('source_binding')
    if binding is None or binding['identity']!={'kind':'ERP_PURCHASE','provider_id':str(provider.pk),'invoice_id':row.pk}:raise AccountingError('Reviewed native invoice binding required.')
    proof_id=uuid5(NS,'posted:'+str(company.pk)+':'+str(row.pk));old=OutboxEvent.objects.filter(pk=proof_id).first()
    if old is None and (source_binding(provider,row)!=binding or row.estado not in {'POR_PAGAR','VENCIDA'}):raise AccountingError('Invoice, supplier or state changed after review.')
    if old is None and OutboxEvent.objects.filter(event_type=ledger.POSTED,aggregate_root=ledger.root(company.pk,doc)).exists():raise AccountingError('Missing native origin proof; do not adopt an unlinked posting.')
    with source_bindings._permit(company.pk,doc,binding,user.pk,'POST'):
        result=ledger.post_fact(company.pk,actor=user,document_id=doc,review_id=review_id,confirmed=confirmed)
    expected={'company_id':str(company.pk),'provider_id':str(provider.pk),'invoice_id':row.pk,'review_id':review_id,'binding_digest':fingerprint(binding),'journal_id':result['journal_id']}
    if old:
        if old.event_type!=POSTED or old.domain!='accounting' or old.version!=1 or old.aggregate_root!=str(company.pk) or old.payload!=expected:raise AccountingError('Native posting origin proof changed.')
    else:OutboxEvent.objects.create(id=proof_id,event_type=POSTED,domain='accounting',aggregate_root=str(company.pk),payload=expected,version=1)
    return {**result,'invoice_id':row.pk,'native_source_verified':True,'source_changed_since_posting':source_binding(provider,row)!=binding}

@transaction.atomic
def purchase_state(*,actor,provider_id,invoice_id):
    user,provider,company=context(actor,provider_id);row=invoice(provider,invoice_id);capture_for(company,row);doc=document(company,row);result=ledger.fact_state(company.pk,actor=user,document_id=doc)
    review=ledger.latest(company.pk,doc);body=ledger.checked(review,ledger.REVIEW,company.pk) if review else None
    binding=body.get('source_binding') if body else source_binding(provider,row)
    captured=capture_for(company,row)
    with source_bindings._permit(company.pk,doc,binding,user.pk,'READ'):
        source_bindings.require(company.pk,doc,binding,user.pk,'READ',captured['document_digest'])
    if result['posted'] is not None:
        native_proof=OutboxEvent.objects.filter(pk=uuid5(NS,'posted:'+str(company.pk)+':'+str(row.pk))).first()
        expected={'company_id':str(company.pk),'provider_id':str(provider.pk),'invoice_id':row.pk,'review_id':str(review.pk),'binding_digest':fingerprint(body['source_binding']),'journal_id':result['posted']['journal_id']}
        if native_proof is None or native_proof.event_type!=POSTED or native_proof.domain!='accounting' or native_proof.version!=1 or native_proof.aggregate_root!=str(company.pk) or native_proof.payload!=expected:raise AccountingError('Native origin proof missing or changed; no reconstructed recovery.')
    return {**result,'invoice_id':row.pk,'native_source_verified':True,'source_matches_review':body is not None and body.get('source_binding')==source_binding(provider,row),'current_invoice_state':row.estado,'document_digest':captured['document_digest'],'review_inputs':review_inputs(body)}

@transaction.atomic
def purchase_sources(*,actor,provider_id,after_id):
    user,provider,company=context(actor,provider_id)
    if after_id is not None:positive(after_id)
    query=FacturaCompra.objects.filter(perfil_id=provider.pk,proveedor__perfil_id=provider.pk).order_by('pk')
    if after_id is not None:query=query.filter(pk__gt=after_id)
    rows=list(query[:21])
    for record in rows:positive(record.pk)
    return {'company_id':str(company.pk),'provider_id':str(provider.pk),'read_only':True,'invoices':[{'invoice_id':r.pk,'supplier_id':r.proveedor_id,'number':r.number,'issue_date':r.issue_date.isoformat(),'subtotal':format(r.subtotal,'.2f'),'tax':format(r.impuestos,'.2f'),'gross':format(r.total,'.2f'),'state':r.estado} for r in rows[:20]],'next_after_id':rows[19].pk if len(rows)>20 else None,'ledger_written':False,'documents_returned':False}

def reversal_context(actor,provider_id,invoice_id):
    user,provider,company=context(actor,provider_id);row=invoice(provider,invoice_id);capture_for(company,row)
    from .purchase_recovery import returns, RETURNED
    if OutboxEvent.objects.filter(event_type=RETURNED,aggregate_root=str(company.pk),payload__body__invoice_id=row.pk).exists() and returns(company,row):raise AccountingError('Purchase has partial returns; do not reverse the full original twice.')
    state=purchase_state(actor=user,provider_id=provider.pk,invoice_id=row.pk)
    if state['posted'] is None:raise AccountingError('Posted native purchase required for reversal.')
    body=ledger.checked(ledger.latest(company.pk,document(company,row)),ledger.REVIEW,company.pk);binding=body.get('source_binding')
    if binding is None or binding['identity']!={'kind':'ERP_PURCHASE','provider_id':str(provider.pk),'invoice_id':row.pk}:raise AccountingError('Native original binding required.')
    return user,provider,company,row,binding

@transaction.atomic
def review_purchase_reversal(*,actor,provider_id,invoice_id,reason_code,evidence_digest,confirmed):
    user,provider,company,row,binding=reversal_context(actor,provider_id,invoice_id);doc=document(company,row)
    with source_bindings._permit(company.pk,doc,binding,user.pk,'REVERSE_REVIEW'):
        result=ledger.review_reversal(company.pk,actor=user,document_id=doc,reason_code=reason_code,evidence_digest=evidence_digest,confirmed=confirmed)
    return {**result,'invoice_id':row.pk,'native_source_verified':True}

@transaction.atomic
def reverse_purchase(*,actor,provider_id,invoice_id,review_id,confirmed):
    user,provider,company,row,binding=reversal_context(actor,provider_id,invoice_id);doc=document(company,row)
    with source_bindings._permit(company.pk,doc,binding,user.pk,'REVERSE_POST'):
        result=ledger.reverse_fact(company.pk,actor=user,document_id=doc,review_id=review_id,confirmed=confirmed)
    return {**result,'invoice_id':row.pk,'native_source_verified':True}

@transaction.atomic
def supplier_sources(*,actor,provider_id,after_id):
    user,provider,company=context(actor,provider_id)
    if after_id is not None:positive(after_id)
    query=Proveedor.objects.filter(perfil_id=provider.pk).order_by('pk')
    if after_id is not None:query=query.filter(pk__gt=after_id)
    rows=list(query[:21])
    for record in rows:positive(record.pk)
    return {'company_id':str(company.pk),'provider_id':str(provider.pk),'read_only':True,'suppliers':[{'supplier_id':r.pk,'name':r.nombre,'identification':r.identificacion} for r in rows[:20]],'next_after_id':rows[19].pk if len(rows)>20 else None,'ledger_written':False,'documents_returned':False,'identity_verified':False}

@transaction.atomic
def purchase_history(*,actor,provider_id,after_id,search):
    """Bounded owner-only read model; legacy rows never acquire invented evidence."""
    user,provider,company=context(actor,provider_id)
    if after_id is not None:positive(after_id)
    if not isinstance(search,str) or len(search)>50 or search!=search.strip() or search and not re.fullmatch('[A-Z0-9][A-Z0-9/_-]{0,49}',search):raise AccountingError('Canonical invoice-number prefix required.')
    query=FacturaCompra.objects.filter(perfil_id=provider.pk,proveedor__perfil_id=provider.pk).select_related('proveedor').order_by('pk')
    if after_id is not None:query=query.filter(pk__gt=after_id)
    if search:query=query.filter(number__startswith=search)
    rows=list(query[:21]);items=[]
    for row in rows[:20]:
        positive(row.pk);key=uuid5(NS,'invoice-capture:'+str(company.pk)+':'+str(row.pk))
        phase='LEGACY_UNRECONCILED';changed=None;journal=None;revision=0
        if OutboxEvent.objects.filter(pk=key).exists():
            capture=capture_for(company,row);state=purchase_state(actor=user,provider_id=provider.pk,invoice_id=row.pk)
            changed=capture['captured_snapshot_digest']!=fingerprint(snapshot(row))
            revision=state['review']['revision'] if state['review'] else 0
            posted=state['posted'];journal=posted['journal_id'] if posted else None
            phase='REVERSED' if posted and posted['reversed'] else 'POSTED' if posted else 'REVIEWED' if state['review'] else 'CAPTURED'
        elif OutboxEvent.objects.filter(pk=source_bindings.reserved_id(company.pk,document(company,row))).exists() or OutboxEvent.objects.filter(event_type=POSTED,payload__company_id=str(company.pk),payload__invoice_id=row.pk).exists():
            raise AccountingError('Native evidence missing; history cannot downgrade a reserved purchase to legacy.')
        items.append({'invoice_id':row.pk,'supplier_id':row.proveedor_id,'number':row.number,'issue_date':row.issue_date.isoformat(),'subtotal':format(row.subtotal,'.2f'),'tax':format(row.impuestos,'.2f'),'gross':format(row.total,'.2f'),'state':row.estado,'accounting_phase':phase,'source_changed':changed,'journal_id':journal,'review_revision':revision})
    return {'company_id':str(company.pk),'provider_id':str(provider.pk),'search':search,'after_id':after_id,'invoices':items,'next_after_id':rows[19].pk if len(rows)>20 else None,'read_only':True,'ledger_written':False,'money_transferred':False,'documents_returned':False,'confirmations_restored':False,'regulatory_verified':False}

def review_return(**kwargs):
    from .purchase_returns import review
    return review(**kwargs)
def post_return(**kwargs):
    from .purchase_returns import post
    return post(**kwargs)
def return_state(**kwargs):
    from .purchase_returns import state
    return state(**kwargs)

def review_return_void(**kwargs):
    from .purchase_return_voids import review
    return review(**kwargs)
def post_return_void(**kwargs):
    from .purchase_return_voids import post
    return post(**kwargs)


def review_item_return(**kwargs):
    from .purchase_item_returns import review
    return review(**kwargs)
def post_item_return(**kwargs):
    from .purchase_item_returns import post
    return post(**kwargs)
def item_return_state(**kwargs):
    from .purchase_item_returns import state
    return state(**kwargs)
def review_item_return_void(**kwargs):
    from .purchase_item_returns import review_void
    return review_void(**kwargs)
def post_item_return_void(**kwargs):
    from .purchase_item_returns import post_void
    return post_void(**kwargs)
