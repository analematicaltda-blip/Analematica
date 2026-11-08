"""Persist server-priced drafts with scoped access and repeat-safe creation."""
import hashlib,hmac,json
from datetime import timedelta
from uuid import UUID
from django.db import transaction,IntegrityError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import APIException,ValidationError
from apps.turismo.models import QuotationDraft
from apps.turismo.services.company_identity import resolve_company
from .quote_preview import preview

class DraftConflict(APIException):
    status_code=409
    default_detail='El borrador no coincide con la solicitud o requiere revisión.'
    default_code='quotation_conflict'


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()


def parse_request(data):
    if not isinstance(data,dict) or set(data)!={'provider_id','customer_id','lines','idempotency_key'}:raise ValidationError('Campos de borrador inválidos.')
    try:
        provider=UUID(str(data['provider_id']));key=UUID(str(data['idempotency_key']))
        raw=data['customer_id']
        if type(raw)is not int and not (isinstance(raw,str) and raw.isascii() and raw.isdecimal()):raise ValueError()
        customer=int(raw)
        if not 1<=customer<=9223372036854775807:raise ValueError()
        lines=data['lines']
        if not isinstance(lines,list) or not 1<=len(lines)<=50:raise ValueError()
        normalized=[];seen=set()
        for line in lines:
            if not isinstance(line,dict) or set(line)!={'product_id','quantity'}:raise ValueError()
            product=UUID(str(line['product_id']));quantity=line['quantity']
            if type(quantity)is not int or not 1<=quantity<=10000 or product in seen:raise ValueError()
            normalized.append({'product_id':str(product),'quantity':quantity});seen.add(product)
    except (ValueError,TypeError):raise ValidationError('Identificadores, líneas o cantidades inválidos.')
    return {'provider_id':str(provider),'customer_id':customer,'lines':sorted(normalized,key=lambda item:item['product_id'])},key


def verify_snapshot(draft):
    if not hmac.compare_digest(digest(draft.snapshot),draft.snapshot_digest):raise DraftConflict()


@transaction.atomic
def create_draft(user,data):
    payload,key=parse_request(data)
    link=resolve_company(user,payload['provider_id'])
    fingerprint=digest(payload)
    query=QuotationDraft.objects.filter(provider_id=link.provider_id,requested_by_id=user.pk,idempotency_key=key)
    existing=query.first()
    if existing:
        if existing.request_digest!=fingerprint or existing.tenant_id!=link.tenant_id:raise DraftConflict()
        verify_snapshot(existing)
        return existing,False
    snapshot=preview(user,payload)
    try:
        with transaction.atomic():
            draft=QuotationDraft.objects.create(provider_id=link.provider_id,tenant_id=link.tenant_id,customer_id=payload['customer_id'],requested_by_id=user.pk,idempotency_key=key,request_digest=fingerprint,snapshot=snapshot,snapshot_digest=digest(snapshot),expires_at=timezone.now()+timedelta(minutes=30))
    except IntegrityError:
        draft=query.get()
        if draft.request_digest!=fingerprint or draft.tenant_id!=link.tenant_id:raise DraftConflict()
        verify_snapshot(draft)
        return draft,False
    return draft,True


def get_draft(user,pk,lock=False):
    query=QuotationDraft.objects.select_for_update() if lock else QuotationDraft.objects.all()
    draft=get_object_or_404(query,pk=pk,requested_by_id=user.pk)
    link=resolve_company(user,draft.provider_id)
    if link.tenant_id!=draft.tenant_id:raise DraftConflict()
    verify_snapshot(draft)
    return draft


@transaction.atomic
def withdraw(user,pk,expected_digest):
    draft=get_draft(user,pk,lock=True)
    if not isinstance(expected_digest,str) or not hmac.compare_digest(draft.snapshot_digest,expected_digest):raise DraftConflict()
    if draft.withdrawn_at is None:
        draft.withdrawn_at=timezone.now();draft.save(update_fields=['withdrawn_at'])
    return draft


def present(draft):
    verify_snapshot(draft)
    status='WITHDRAWN' if draft.withdrawn_at else ('EXPIRED' if draft.expires_at<=timezone.now() else 'DRAFT')
    return {'id':str(draft.pk),'provider_id':str(draft.provider_id),'customer_id':draft.customer_id,'status':status,'created_at':draft.created_at,'expires_at':draft.expires_at,'withdrawn_at':draft.withdrawn_at,'digest':draft.snapshot_digest,'preview':draft.snapshot}
