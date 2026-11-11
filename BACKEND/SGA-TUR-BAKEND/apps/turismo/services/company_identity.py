"""Validate authoritative records on each access. No public provisioning endpoint."""
import re
from datetime import timedelta,datetime
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied,ValidationError
from apps.core_erp.tenancy.models import Tenant
from ..models import BusinessProfile,TourismProvider,VerifiedCompanyLink


def valid_link(link,user):
    now=timezone.now()
    if not user or not user.is_authenticated or not user.is_active:return False
    actual=get_user_model().objects.filter(pk=user.pk,is_active=True).first()
    reviewer=get_user_model().objects.filter(pk=link.reviewed_by_id,is_active=True,is_superuser=True).first()
    if actual is None or reviewer is None or reviewer.pk==link.administrator_id:return False
    if not isinstance(link.verified_at,datetime) or not isinstance(link.valid_until,datetime) or not timezone.is_aware(link.verified_at) or not timezone.is_aware(link.valid_until):return False
    if link.revoked_at or not link.verified_at<=now<link.valid_until:return False
    if link.administrator_id!=user.pk or link.provider.owner_id!=user.pk:return False
    if not link.provider.is_active or link.provider.status!='ACTIVE':return False
    if not link.tenant.is_active or link.tenant.state!='ACTIVE':return False
    # A transfer of ownership or legal identity invalidates the old review.
    legal=BusinessProfile.objects.filter(provider_id=link.provider_id).first()
    return bool(legal and legal.is_active and legal.tax_id and legal.tax_id==link.tenant.tax_id==link.verified_tax_id and isinstance(link.evidence_digest,str) and re.fullmatch('[0-9a-f]{64}',link.evidence_digest))


def resolve_company(user,provider_id):
    link=VerifiedCompanyLink.objects.select_related('provider','tenant','reviewed_by').filter(provider_id=provider_id).first()
    if link is None or not valid_link(link,user):raise PermissionDenied('Empresa sin vínculo vigente y administrador titular verificado.')
    return link


@transaction.atomic
def review_link(*,operator,provider_id,tenant_id,evidence_digest,valid_until,apply=False):
    """Explicit trusted operator review; dry-run unless apply=True, no reassign/renew."""
    operator_id=getattr(operator,'pk',None)
    if operator_id is None:raise PermissionDenied('Se requiere un operador de identidad autorizado.')
    now=timezone.now()
    if not isinstance(evidence_digest,str) or not re.fullmatch('[0-9a-f]{64}',evidence_digest):raise ValidationError('Huella de evidencia inválida.')
    if not isinstance(valid_until,datetime) or not timezone.is_aware(valid_until) or not now<valid_until<=now+timedelta(days=30):raise ValidationError('Vigencia máxima de treinta días.')
    # Match the order used by financial operations: company, then provider.
    tenant=Tenant.objects.select_for_update().get(pk=tenant_id)
    provider=TourismProvider.objects.select_for_update(of=('self',)).select_related('owner').get(pk=provider_id)
    operator=get_user_model().objects.select_for_update().filter(pk=operator_id,is_active=True,is_superuser=True).first()
    if operator is None:raise PermissionDenied('Se requiere un operador de identidad autorizado.')
    if operator.pk==provider.owner_id:raise PermissionDenied('La revisión debe ser independiente del administrador titular.')
    link=VerifiedCompanyLink(provider=provider,tenant=tenant,administrator=provider.owner,reviewed_by=operator,verified_tax_id=tenant.tax_id,evidence_digest=evidence_digest,verified_at=now,valid_until=valid_until)
    if not valid_link(link,provider.owner):raise ValidationError('Identidad tributaria, titularidad o estado empresarial no válido.')
    if VerifiedCompanyLink.objects.filter(provider=provider).exists() or VerifiedCompanyLink.objects.filter(tenant=tenant).exists():raise ValidationError('Existe un vínculo previo; requiere revisión de recuperación, sin sobrescritura.')
    if apply:link.save(force_insert=True)
    return link
