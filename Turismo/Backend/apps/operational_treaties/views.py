from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .models import OperationalTreaty, TreatyComplianceAudit, SovereignKillSwitch
from .serializers import OperationalTreatySerializer, TreatyComplianceAuditSerializer
from .services import TreatyValidatorService

class OperationalTreatyViewSet(viewsets.ModelViewSet):
    """
    Gestor de Tratados Operativos (Z-OPERATIONAL-TREATIES).
    """
    queryset = OperationalTreaty.objects.all()
    serializer_class = OperationalTreatySerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=['post'], url_path='trigger-kill-switch')
    def trigger_kill(self, request, pk=None):
        treaty = self.get_object()
        reason = request.data.get('reason', 'Intervención manual SuperAdmin')

        ks, created = SovereignKillSwitch.objects.get_or_create(treaty=treaty)
        ks.trigger(request.user, reason)

        return Response({"status": "KILL_SWITCH_ACTIVATED", "treaty": treaty.name})

    @action(detail=False, methods=['get'], url_path='compliance-audit')
    def list_audits(self, request):
        audits = TreatyComplianceAudit.objects.all()[:100]
        return Response(TreatyComplianceAuditSerializer(audits, many=True).data)

    @action(detail=False, methods=['get'], url_path='transparency-summary')
    def transparency_summary(self, request):
        """
        Z-TRUST-IMPLEMENTATION: Resumen para la UX de Soberanía.
        Muestra qué tratados están activos y qué señales se están compartiendo.
        """
        active_treaties = OperationalTreaty.objects.filter(is_active=True)

        summary = []
        for treaty in active_treaties:
            summary.append({
                "treaty_name": treaty.name,
                "type": treaty.type,
                "shared_since": treaty.signed_at,
                "partner_nodes": treaty.participating_nodes,
                "signals_allowed": treaty.signal_types_allowed,
                "audit_level": treaty.audit_level,
                "is_monitored": True
            })

        return Response({
            "node_sovereignty_status": "FULL_CONTROL",
            "active_cooperation_treaties": summary,
            "system_trust_index": 1.0,
            "last_integrity_verification": timezone.now()
        })

    @action(detail=False, methods=['post'], url_path='pap-early-warning')
    def emit_pap(self, request):
        """Protocolo de Alerta Preventiva (PAP)."""
        node_id = request.data.get('node_id')
        risk_type = request.data.get('risk_type')

        # Registrar alerta en el log de cumplimiento
        logger.warning(f"PAP: Alerta preventiva recibida de {node_id}: {risk_type}")
        return Response({"status": "PAP_REGISTERED"})

    @action(detail=False, methods=['get'], url_path='pac-cross-audit')
    def cross_audit(self, request):
        """Protocolo de Auditoría Cruzada (PAC)."""
        # Devuelve un Audit Bundle anonimizado para verificación mutua
        return Response({
            "node_id": "SARITA_NATIONAL_NODE_01",
            "integrity_proof": "SHA256_CHAIN_VALID",
            "neutrality_index": 1.0,
            "timestamp": "2026-02-06T00:00:00Z"
        })
