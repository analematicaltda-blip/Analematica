"""Independent reviewed source binding and native accounting authority."""
from datetime import datetime,timezone,timedelta
from .crm import CRMError,digest
from .source_protocol import verify
from .sales_models import SaleSourceBinding
from .opportunities import uuid_ref

def review_binding(*,operator,provider_id,proof,valid_until,support_digest,apply=False):
    from apps.turismo.models import VerifiedCompanyLink
    from django.contrib.auth import get_user_model
    from .identity import resolve_access
    import re
    context,_=verify(proof);uuid_ref(str(provider_id));row=VerifiedCompanyLink.objects.select_related('administrator','tenant','reviewed_by').filter(provider_id=provider_id,revoked_at=None,valid_until__gt=datetime.now(timezone.utc)).first()
    reviewer=get_user_model().objects.filter(pk=getattr(operator,'pk',None),is_active=True).first()
    if not row or not reviewer or reviewer.pk!=row.reviewed_by_id or reviewer.pk==row.administrator_id:raise CRMError('INDEPENDENT_COMPANY_REVIEWER_REQUIRED',403)
    owner=resolve_access(row.administrator,str(provider_id))
    if not owner.principal['is_manager']:raise CRMError('NATIVE_COMPANY_OWNER_REQUIRED',403)
    if not isinstance(valid_until,datetime) or valid_until.tzinfo is None or not datetime.now(timezone.utc)<valid_until<=min(datetime.now(timezone.utc)+timedelta(days=30),row.valid_until):raise CRMError('INVALID_SOURCE_BINDING_VALIDITY')
    if not isinstance(support_digest,str) or not re.fullmatch('[a-f0-9]{64}',support_digest):raise CRMError('SALE_SOURCE_REVIEW_SUPPORT_REQUIRED')
    if SaleSourceBinding.objects.filter(source_system='sga-cd',source_scope=context['scope'],source_actor=context['actor'],provider_ref=str(provider_id)).exists():raise CRMError('SOURCE_BINDING_RECONCILIATION_REQUIRED',409)
    binding=SaleSourceBinding(source_system='sga-cd',source_scope=context['scope'],source_actor=context['actor'],source_role_fingerprint=context['role_fingerprint'],provider_ref=str(provider_id),tenant_ref=str(row.tenant_id),actor_ref=str(row.administrator_id),reviewer_ref=str(reviewer.pk),support_digest=support_digest,valid_until=valid_until)
    if apply:binding.save()
    return binding

def binding(context,crm):
    from django.contrib.auth import get_user_model
    from apps.turismo.models import VerifiedCompanyLink
    crm.authorize();row=SaleSourceBinding.objects.filter(source_system='sga-cd',source_scope=context['scope'],source_actor=context['actor'],source_role_fingerprint=context['role_fingerprint'],provider_ref=crm.store.provider,tenant_ref=crm.store.scope,actor_ref=crm.actor,revoked_at=None,valid_until__gt=datetime.now(timezone.utc)).first()
    if not row or not get_user_model().objects.filter(pk=row.reviewer_ref,is_active=True).exists():raise CRMError('REVIEWED_SALE_SOURCE_BINDING_REQUIRED',403)
    link=VerifiedCompanyLink.objects.filter(provider_id=crm.store.provider,tenant_id=crm.store.scope,administrator_id=crm.actor,reviewed_by_id=row.reviewer_ref,revoked_at=None,valid_until__gt=datetime.now(timezone.utc)).first()
    if not link:raise CRMError('REVIEWED_SALE_SOURCE_BINDING_REQUIRED',403)
    return row


def binding_snapshot(row):
    return {key:str(getattr(row,key)) if getattr(row,key) is not None else None for key in ('id','source_system','source_scope','source_actor','source_role_fingerprint','provider_ref','tenant_ref','actor_ref','reviewer_ref','support_digest','valid_until','revoked_at')}

def revise_binding(*,operator,binding_id,proof,expected_digest,valid_until,support_digest,revoke=False,apply=False):
    """Independent review, optimistic comparison and append-only audit; no self-service grant."""
    from django.db import transaction
    from apps.turismo.models import VerifiedCompanyLink
    from apps.core_erp.outbox_models import OutboxEvent
    from django.contrib.auth import get_user_model
    from .identity import resolve_access
    import re,uuid
    context,_=verify(proof)
    if type(revoke)!=bool or not isinstance(support_digest,str) or not re.fullmatch('[a-f0-9]{64}',support_digest):raise CRMError('SALE_SOURCE_REVIEW_SUPPORT_REQUIRED')
    with transaction.atomic():
        row=SaleSourceBinding.objects.select_for_update().filter(pk=uuid_ref(str(binding_id))).first()
        if not row:raise CRMError('SOURCE_BINDING_NOT_FOUND',404)
        before=binding_snapshot(row)
        if digest(before)!=expected_digest:raise CRMError('SOURCE_BINDING_REVISION_CONFLICT',409)
        if (context['scope'],context['actor'])!=(row.source_scope,row.source_actor):raise CRMError('SOURCE_BINDING_CONTEXT_MISMATCH',403)
        link=VerifiedCompanyLink.objects.filter(provider_id=row.provider_ref,tenant_id=row.tenant_ref,administrator_id=row.actor_ref,revoked_at=None,valid_until__gt=datetime.now(timezone.utc)).first()
        reviewer=get_user_model().objects.filter(pk=getattr(operator,'pk',None),is_active=True).first()
        if not link or not reviewer or reviewer.pk!=link.reviewed_by_id or reviewer.pk==link.administrator_id:raise CRMError('INDEPENDENT_COMPANY_REVIEWER_REQUIRED',403)
        if not resolve_access(link.administrator,row.provider_ref).principal['is_manager']:raise CRMError('NATIVE_COMPANY_OWNER_REQUIRED',403)
        if not revoke and (not isinstance(valid_until,datetime) or valid_until.tzinfo is None or not datetime.now(timezone.utc)<valid_until<=min(datetime.now(timezone.utc)+timedelta(days=30),link.valid_until)):raise CRMError('INVALID_SOURCE_BINDING_VALIDITY')
        row.reviewer_ref=str(reviewer.pk);row.support_digest=support_digest;row.source_role_fingerprint=context['role_fingerprint'];row.revoked_at=datetime.now(timezone.utc) if revoke else None
        if not revoke:row.valid_until=valid_until
        after=binding_snapshot(row)
        if apply:
            row.save()
            OutboxEvent.objects.create(id=uuid.uuid4(),event_type='commercial.sale.source-binding.reviewed.v1',domain='commercial',aggregate_root=str(row.pk),payload={'before':before,'after':after,'before_digest':digest(before),'after_digest':digest(after),'reviewer_ref':str(reviewer.pk),'revoke':revoke},version=1)
        return row
