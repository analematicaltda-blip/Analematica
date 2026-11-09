"""Trusted internal SST operations; no inferred company or fabricated archive.
Callers must supply the authenticated actor ID and explicitly selected provider.
This module does not grant remote-control or financial authorization.
"""
import hashlib
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError
from apps.audit.models import AuditLog
from apps.turismo.models import TourismProvider
from apps.turismo.services.company_identity import resolve_company
from apps.core_erp.accounting.validation import lock_company
from .models import IncidenteLaboral


def _context(usuario_id, provider_id):
    user = get_user_model().objects.filter(pk=usuario_id, is_active=True).first()
    if user is None or getattr(user, 'is_agent', False):
        raise PermissionDenied('Se requiere un titular personal activo.')
    provider = TourismProvider.objects.filter(pk=provider_id, owner_id=user.pk, is_active=True, status='ACTIVE').first()
    if provider is None:
        raise PermissionDenied('Empresa no autorizada.')
    provider = TourismProvider.objects.select_for_update().get(pk=provider.pk)
    if provider.owner_id != user.pk or not provider.is_active or provider.status != 'ACTIVE':
        raise PermissionDenied('El contexto empresarial cambió.')
    company = resolve_company(user, provider.pk).tenant
    lock_company(company.pk)
    resolve_company(user, provider.pk)
    return user, provider


class SargentoSST:
    @staticmethod
    @transaction.atomic
    def registrar_incidente(datos: dict, usuario_id, *, provider_id):
        from .serializers import IncidenteLaboralSerializer
        user, provider = _context(usuario_id, provider_id)
        if not isinstance(datos, dict) or str(datos.get('perfil_id')) != str(provider.pk):
            raise ValidationError('La empresa del incidente contradice el contexto autorizado.')
        serializer = IncidenteLaboralSerializer(data={
            'tipo': datos.get('tipo'), 'fecha_hora': datos.get('fecha_hora'),
            'lugar': datos.get('lugar'), 'descripcion_hechos': datos.get('descripcion'),
            'gravedad': datos.get('gravedad'),
        }, context={'sst_provider': provider})
        serializer.is_valid(raise_exception=True)
        incident = serializer.save(provider_id=provider.pk)
        AuditLog.objects.create(user=user, username=user.username, action='SST_INCIDENT_REGISTERED',
                                details={'provider_id': str(provider.pk), 'incident_id': str(incident.pk)})
        # No company_id=1 placeholder, fake document or assertion of containment.
        return {'status': 'REGISTERED', 'id': incident.pk, 'archive_created': False,
                'operational_containment_applied': False}

    @staticmethod
    @transaction.atomic
    def bloquear_operacion_por_riesgo(proceso_id: str, motivo: str, usuario_id, *, provider_id):
        from ..models import ProcesoOperativo
        user, provider = _context(usuario_id, provider_id)
        if not isinstance(motivo, str) or not 1 <= len(motivo.strip()) <= 2000:
            raise ValidationError('Motivo explícito y acotado requerido.')
        process = ProcesoOperativo.objects.select_for_update().get(pk=proceso_id, provider_id=provider.pk)
        if process.estado in {'COMPLETADO', 'FALLIDO'}:
            raise ValidationError('No se reescribe el estado de un proceso finalizado.')
        from ..state_service import transition
        result=transition(usuario_id=user.pk,provider_id=provider.pk,kind='ProcesoOperativo',
            operation_id=process.pk,expected_state=process.estado,new_state='SUSPENDIDO',
            reason=motivo,confirmed=True,audit_action='OPERATIONAL_SST_BLOCK')
        replay=result['replayed']
        return {'status': 'BLOCKED', 'proceso': str(process.pk), 'replayed': replay,
                'medical_qualification_verified': False}
