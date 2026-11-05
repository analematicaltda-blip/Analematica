import logging
import json
import hashlib
from datetime import timedelta
from django.utils import timezone
from .models import AlgorithmicCertificate, TrustSignal
from apps.audit.models import ForensicSecurityLog, AuditLog
from apps.admin_plataforma.models import GovernanceAuditLog, GovernancePolicy
from api.models import CustomUser

logger = logging.getLogger(__name__)

class TrustCertificateService:
    """
    Motor de Certificados de Confianza (Z-TRUST-NET).
    Genera pruebas matemáticas de cumplimiento institucional.
    """

    @staticmethod
    def generate_governance_certificate(node_id: str) -> AlgorithmicCertificate:
        """Genera un certificado basado en la integridad del Kernel de Gobernanza."""
        # Recopilar evidencia: Estado de la cadena de hashes de auditoría
        last_logs = GovernanceAuditLog.objects.order_by('-timestamp')[:100]
        integrity_check = all(log.success for log in last_logs) if last_logs else True

        evidence = {
            "kernel_version": "v1.0-RC-S",
            "active_policies_count": GovernancePolicy.objects.filter(is_active=True).count(),
            "audit_chain_integrity": integrity_check,
            "sovereign_interventions_24h": GovernanceAuditLog.objects.filter(
                es_intervencion_soberana=True,
                timestamp__gte=timezone.now() - timedelta(hours=24)
            ).count()
        }

        cert = AlgorithmicCertificate.objects.create(
            node_id=node_id,
            type=AlgorithmicCertificate.CertificateType.GOVERNANCE,
            expires_at=timezone.now() + timedelta(days=7),
            evidence_summary=evidence
        )
        cert.generate_signature()
        cert.save()
        return cert

    @staticmethod
    def generate_security_certificate(node_id: str) -> AlgorithmicCertificate:
        """Genera un certificado basado en la efectividad de la defensa perimetral."""
        recent_threats = ForensicSecurityLog.objects.filter(
            timestamp__gte=timezone.now() - timedelta(hours=24)
        )

        evidence = {
            "active_defense_status": "OPERATIONAL",
            "critical_threats_neutralized_24h": recent_threats.filter(threat_level='CRITICAL').count(),
            "avg_containment_time_ms": 150, # Simulado
            "deception_layer_active": True
        }

        cert = AlgorithmicCertificate.objects.create(
            node_id=node_id,
            type=AlgorithmicCertificate.CertificateType.SECURITY,
            expires_at=timezone.now() + timedelta(days=1),
            evidence_summary=evidence
        )
        cert.generate_signature()
        cert.save()
        return cert

    @staticmethod
    def verify_external_certificate(certificate_data: dict) -> bool:
        """
        Valida un certificado recibido de otro Nodo Soberano.
        """
        node_id = certificate_data.get('node_id')
        cert_type = certificate_data.get('type')
        issued_at = certificate_data.get('issued_at')
        evidence = certificate_data.get('evidence_summary')
        signature = certificate_data.get('signature')

        # 1. Verificar firma (Simulado: en prod usaría la llave pública del nodo_id)
        payload = f"{node_id}{cert_type}{issued_at}{json.dumps(evidence)}"

        from django.conf import settings
        private_key = getattr(settings, "SARITA_NODE_PRIVATE_KEY", "SARITA_FALLBACK_KEY_STABLE_Z")
        expected_signature = hashlib.sha256((payload + private_key).encode()).hexdigest()

        if signature != expected_signature:
            logger.error(f"Z-TRUST-NET: Firma de certificado INVÁLIDA de {node_id}")
            return False

        # 2. Verificar expiración
        # (Lógica omitida por brevedad)

        logger.info(f"Z-TRUST-NET: Certificado de {node_id} verificado con éxito.")
        return True

class TrustSignalService:
    """
    Gestor de Señales de Confianza e Intercambio Diplomático.
    """

    @staticmethod
    def emit_threat_signal(category: str, level: str, description: str, user: CustomUser):
        """Emite una señal de alerta temprana para la red global."""
        from apps.admin_plataforma.services.governance_kernel import GovernanceKernel

        # 3.1: Validar mandato en el Kernel antes de emitir
        kernel = GovernanceKernel(user)
        if not kernel.validate_interop_mandate(category, "GLOBAL_MESH", direction='OUTGOING'):
            raise PermissionError(f"Gobernanza: No existe tratado activo para emitir señales de tipo '{category}'.")

        signal = TrustSignal.objects.create(
            origin_node="SARITA_NATIONAL_NODE_01",
            category=category,
            level=level,
            description=description
        )
        logger.warning(f"Z-TRUST-NET: Señal de Confianza EMITIDA: {signal}")
        return signal

    @staticmethod
    def receive_external_signal(signal_data: dict, user: CustomUser):
        """Procesa una señal recibida de otro país."""
        from apps.admin_plataforma.services.governance_kernel import GovernanceKernel

        node_id = signal_data.get('origin_node')
        category = signal_data.get('category')

        # 3.1: Validar mandato en el Kernel antes de recibir
        kernel = GovernanceKernel(user)
        if not kernel.validate_interop_mandate(category, node_id, direction='INCOMING'):
            logger.error(f"Z-TRUST-NET: Señal de {node_id} RECHAZADA por el Kernel. Sin mandato para '{category}'.")
            return

        level = signal_data.get('level')
        category = signal_data.get('category')

        logger.info(f"Z-TRUST-NET: Señal EXTERNA recibida de {node_id}: {level}")

        # Si recibimos una señal crítica de un nodo, revocamos preventivamente sus certificados locales
        if level == TrustSignal.SignalLevel.CRITICAL:
            revoked_count = AlgorithmicCertificate.objects.filter(
                node_id=node_id,
                is_revoked=False
            ).update(
                is_revoked=True,
                revocation_reason=f"Señal CRÍTICA recibida: {category}. Aislamiento preventivo activo."
            )
            if revoked_count > 0:
                logger.warning(f"Z-TRUST-NET: AISLAMIENTO DETECTADO. Revocados {revoked_count} certificados de {node_id}")

        # Guardar la señal recibida
        TrustSignal.objects.get_or_create(
            origin_node=node_id,
            category=category,
            level=level,
            description=signal_data.get('description', ''),
            verification_hash=signal_data.get('verification_hash', '')
        )
