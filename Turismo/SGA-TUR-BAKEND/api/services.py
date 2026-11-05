from .models import Publicacion, CustomUser
from rest_framework.exceptions import PermissionDenied, ValidationError

def aprobar_publicacion(publicacion_id: int, usuario: CustomUser) -> Publicacion:
    """
    Aprueba una publicación, moviéndola al siguiente estado en el flujo de trabajo.
    - Un FUNCIONARIO_DIRECTIVO la mueve de PENDIENTE_DIRECTIVO a PENDIENTE_ADMIN.
    - Un ADMIN la mueve de PENDIENTE_ADMIN a PUBLICADO.
    """
    try:
        publicacion = Publicacion.objects.get(pk=publicacion_id)
    except Publicacion.DoesNotExist:
        raise ValidationError(f"La publicación con id {publicacion_id} no existe.")

    if publicacion.estado == 'PENDIENTE_DIRECTIVO' and usuario.role == CustomUser.Role.FUNCIONARIO_DIRECTIVO:
        publicacion.estado = 'PENDIENTE_ADMIN'
    elif publicacion.estado == 'PENDIENTE_ADMIN' and usuario.role == CustomUser.Role.ADMIN:
        publicacion.estado = 'PUBLICADO'
    else:
        raise PermissionDenied("No tiene permiso para realizar esta acción o la publicación no está en el estado correcto.")

    publicacion.save()
    return publicacion

def rechazar_publicacion(publicacion_id: int, usuario: CustomUser) -> Publicacion:
    """
    Rechaza una publicación y la devuelve al estado BORRADOR.
    Solo puede ser ejecutado por un ADMIN o FUNCIONARIO_DIRECTIVO.
    """
    if not (usuario.role == CustomUser.Role.ADMIN or usuario.role == CustomUser.Role.FUNCIONARIO_DIRECTIVO):
        raise PermissionDenied("No tiene permiso para realizar esta acción.")

    try:
        publicacion = Publicacion.objects.get(pk=publicacion_id)
    except Publicacion.DoesNotExist:
        raise ValidationError(f"La publicación con id {publicacion_id} no existe.")

    publicacion.estado = 'BORRADOR'
    publicacion.save()
    return publicacion

def enviar_para_aprobacion(publicacion_id: int, usuario: CustomUser) -> Publicacion:
    """
    Envía una publicación para su aprobación, moviéndola al estado PENDIENTE_DIRECTIVO.
    El usuario debe ser el autor de la publicación o un funcionario.
    """
    try:
        publicacion = Publicacion.objects.get(pk=publicacion_id)
    except Publicacion.DoesNotExist:
        raise ValidationError(f"La publicación con id {publicacion_id} no existe.")

    # Un funcionario puede enviar cualquier publicación para aprobación.
    # Un autor solo puede enviar sus propias publicaciones.
    es_funcionario = usuario.role in [CustomUser.Role.ADMIN, CustomUser.Role.FUNCIONARIO_DIRECTIVO, CustomUser.Role.FUNCIONARIO_PROFESIONAL]
    es_autor = publicacion.autor == usuario

    if not (es_funcionario or es_autor):
        raise PermissionDenied("No tiene permiso para enviar esta publicación para aprobación.")

    publicacion.estado = 'PENDIENTE_DIRECTIVO'
    publicacion.save()
    return publicacion

import hashlib
import json
from apps.audit.models import ForensicSecurityLog
from rest_framework.authtoken.models import Token
import logging

logger = logging.getLogger(__name__)

class DefenseService:
    """
    Servicio Central de Contención y Defensa S-0.3 / S-1.1.
    Responsable de neutralizar ataques y registrar evidencia forense.
    Organizado en Anillos de Defensa.
    """

    # --- ANILLO 1: OBSERVACIÓN INTELIGENTE (S-1.2) ---
    @staticmethod
    def classify_event(attack_vector, user=None):
        """
        Clasifica la amenaza según el vector y el contexto (S-1.2).
        """
        if attack_vector in ["INVALID_INTENTION_INJECTION", "GOVERNANCE_AUTHORITY_VIOLATION"]:
            return 'CRITICAL' # 🔴 Ataque activo
        if attack_vector in ["XSS_ATTEMPT", "DOM_MUTATION"]:
            return 'CRITICAL'
        if attack_vector in ["BRUTE_FORCE", "RATE_LIMIT_EXCEEDED"]:
            return 'HIGH'     # 🟠 Riesgo sistémico
        if attack_vector in ["UNKNOWN_ROUTE_SCAN"]:
            return 'MEDIUM'   # 🟡 Riesgo leve
        return 'LOW'          # 🟢 Ruido

    @staticmethod
    def neutralize_threat(user, attack_vector, payload, headers, threat_level=None):
        """
        Neutraliza una amenaza activa mediante cuarentena y registro forense.
        """
        source_ip = headers.get('REMOTE_ADDR') or headers.get('HTTP_X_FORWARDED_FOR')

        # S-1.2: Clasificación automática si no se provee nivel
        effective_level = threat_level or DefenseService.classify_event(attack_vector, user)

        # 1. Registro Forense Firmado (Filtrando secretos)
        SENSITIVE_HEADERS = ['HTTP_AUTHORIZATION', 'HTTP_COOKIE', 'HTTP_X_API_KEY', 'X-Api-Key', 'Authorization', 'Cookie']
        safe_headers = {k: v for k, v in headers.items() if isinstance(v, str) and k.upper() not in SENSITIVE_HEADERS}

        # S-0.3: Delegar creación y firma atómica al método de clase
        log_entry = ForensicSecurityLog.log_event(
            threat_level=effective_level,
            attack_vector=attack_vector,
            payload_captured=payload,
            headers_captured=safe_headers,
            action_taken="SESSION_QUARANTINE, TOKEN_INVALIDATED" if user and not user.is_anonymous else "IP_BLOCK_RECOMMENDED",
            user=user if user and not user.is_anonymous else None,
            source_ip=source_ip
        )

        # 3. Contención: Invalidar Sesión si hay usuario
        if user and not user.is_anonymous:
            # Eliminar todos los tokens del usuario para forzar logout global
            Token.objects.filter(user=user).delete()
            logger.warning(f"S-0: Usuario {user.username} puesto en CUARENTENA por {attack_vector}.")

        # 4. Notificar al Sovereignty Center (vía Logs por ahora)
        logger.error(f"S-0 CRITICAL: Ataque detectado y contenido. Vector: {attack_vector}. IP: {source_ip}")

        # S-1.3: Disparar respuesta autónoma si aplica
        if effective_level in ['HIGH', 'CRITICAL']:
            AutonomousDefenseManager.trigger_response(log_entry)

        return log_entry.id


class AutonomousDefenseManager:
    """
    Gestor de Respuestas Autónomas S-1.3 (Anillo 2).
    Ejecuta acciones de contención sin intervención humana dentro de límites duros.
    """

    @staticmethod
    def trigger_response(log_entry):
        """
        Determina y ejecuta la respuesta óptima ante un log de seguridad.
        """
        from apps.ecosystem_optimization.models import AutonomousExecutionLog, AutonomousAction
        from apps.admin_plataforma.models import GovernancePolicy

        # 1. Verificar si el Kill-Switch de Autonomía está activo (Ring 0 check)
        if GovernancePolicy.objects.filter(name="KILL_SWITCH_AUTONOMY", is_active=True).exists():
            logger.warning(f"S-1.3: Respuesta autónoma ABORTADA. Kill-Switch activo para {log_entry.id}")
            return

        # 2. Seleccionar respuesta según nivel
        response_action = "NONE"
        xai_explanation = ""

        if log_entry.threat_level == 'CRITICAL':
            # Ring 3: Escalamiento forzado (S-1.6)
            response_action = "FORCE_SYSTEM_FREEZE_PROPOSAL"
            xai_explanation = "Amenaza crítica detectada. Se propone congelamiento sistémico inmediato para proteger la integridad del Kernel."
            AutonomousDefenseManager._escalate_to_ring3(log_entry, xai_explanation)

        elif log_entry.threat_level == 'HIGH':
            # Ring 2: Acción autónoma
            response_action = "HARDEN_RATE_LIMITS"
            xai_explanation = "Actividad de alto riesgo detectada. Endurecimiento preventivo de límites de petición para el origen."
            AutonomousDefenseManager._apply_ring2_containment(log_entry, response_action, xai_explanation)

        # 3. Registrar ejecución de defensa (Auditoría Ring 1)
        # (Aquí se usaría AutonomousExecutionLog de optimization)

    @staticmethod
    def _apply_ring2_containment(log_entry, action_name, explanation):
        """
        Aplica acciones de contención del Anillo 2.
        """
        logger.info(f"S-1.3 (Ring 2): Aplicando {action_name} ante {log_entry.attack_vector}. XAI: {explanation}")
        # En una implementación real, aquí se interactuaría con Redis/Firewall/Middleware
        # para aplicar el rate limit o bloqueo de IP.

    @staticmethod
    def _escalate_to_ring3(log_entry, explanation):
        """
        Escala a intervención humana (Anillo 3 / S-1.6).
        Genera una propuesta estratégica para el SuperAdmin.
        """
        from apps.decision_intelligence.models import StrategyProposal

        # S-1.4: Aprendizaje Defensivo (Generación de propuesta desde el evento)
        StrategyProposal.objects.create(
            domain='SISTEMICO',
            nivel_riesgo='HIGH',
            nivel_urgencia='CRITICAL',
            decision_level=3, # Estratégica
            contexto_detectado=f"Ataque detectado: {log_entry.attack_vector} desde IP {log_entry.source_ip}.",
            riesgo_actual="Compromiso potencial de la integridad del Kernel de Gobernanza.",
            oportunidad_detectada="Contención total de la amenaza y registro de patrón forense.",
            accion_sugerida={
                "intention": "SYSTEM_ATTACK_MODE_TOGGLE",
                "parameters": {"active": True, "reason": f"Auto-escalation S-1.6 from {log_entry.id}"}
            },
            impacto_estimado="Cese de todas las operaciones de escritura; modo solo lectura activo.",
            nivel_confianza=0.95,
            agent_id="SARITA_DEFENSE_SENTINEL",
            agent_id_type="DEFENSE"
        )
        logger.warning(f"S-1.6 (Ring 3): Amenaza ESCALADA a SuperAdmin. Propuesta generada para {log_entry.id}")
