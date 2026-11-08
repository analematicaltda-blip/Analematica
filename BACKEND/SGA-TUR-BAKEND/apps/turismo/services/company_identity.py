"""Validate authoritative records on each access. No public provisioning endpoint."""
import re
from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied,ValidationError
from apps.core_erp.tenancy.models import Tenant
from ..models import BusinessProfile,TourismProvider,VerifiedCompanyLink


def valid_link(link,user):
    now=timezone.now()
    if not user or not user.is_authenticated or not user.is_active:return False
    if not link.reviewed_by.is_active or not link.reviewed_by.is_superuser:return False
    if link.revoked_at or not link.verified_at<=now<link.valid_until:return False
    if link.administrator_id!=user.pk or link.provider.owner_id!=user.pk:return False
    if not link.provider.is_active or link.provider.status!='ACTIVE':return False
    if not link.tenant.is_active or link.tenant.state!='ACTIVE':return False
    # A transfer of ownership or legal identity invalidates the old review.
    legal=BusinessProfile.objects.filter(provider_id=link.provider_id).first()
    return bool(legal and legal.is_active and legal.tax_id and legal.tax_id==link.tenant.tax_id==link.verified_tax_id and re.fullmatch('[0-9a-f]{64}',link.evidence_digest))


def resolve_company(user,provider_id):
    link=VerifiedCompanyLink.objects.select_related('provider','tenant','reviewed_by').filter(provider_id=provider_id).first()
    if link is None or not valid_link(link,user):raise PermissionDenied('Empresa sin vínculo vigente y administrador titular verificado.')
    return link


@transaction.atomic
def review_link(*,operator,provider_id,tenant_id,evidence_digest,valid_until,apply=False):
    """Explicit trusted operator review; dry-run unless apply=True, no reassign/renew."""
    if not operator.is_active or not operator.is_superuser:raise PermissionDenied('Se requiere un operador de identidad autorizado.')
    now=timezone.now()
    if not isinstance(evidence_digest,str) or not re.fullmatch('[0-9a-f]{64}',evidence_digest):raise ValidationError('Huella de evidencia inválida.')
    if not timezone.is_aware(valid_until) or not now<valid_until<=now+timedelta(days=30):raise ValidationError('Vigencia máxima de treinta días.')
    provider=TourismProvider.objects.select_for_update().select_related('owner').get(pk=provider_id)
    tenant=Tenant.objects.select_for_update().get(pk=tenant_id)
    if operator.pk==provider.owner_id:raise PermissionDenied('La revisión debe ser independiente del administrador titular.')
    link=VerifiedCompanyLink(provider=provider,tenant=tenant,administrator=provider.owner,reviewed_by=operator,verified_tax_id=tenant.tax_id,evidence_digest=evidence_digest,verified_at=now,valid_until=valid_until)
    if not valid_link(link,provider.owner):raise ValidationError('Identidad tributaria, titularidad o estado empresarial no válido.')
    if VerifiedCompanyLink.objects.filter(provider=provider).exists() or VerifiedCompanyLink.objects.filter(tenant=tenant).exists():raise ValidationError('Existe un vínculo previo; requiere revisión de recuperación, sin sobrescritura.')
    if apply:link.save(force_insert=True)
    return link
