import uuid
import logging
import hashlib
from datetime import datetime
from django.utils import timezone
from .models import GovernanceAuditLog, AgentInteraction

logger = logging.getLogger(__name__)

class PCAMessage:
    """
    Estructura formal de un mensaje del Protocolo de Coordinación de Agentes.
    """
    def __init__(self, correlation_id, sender_id, role, authority_level, interaction_type, payload):
        self.message_id = uuid.uuid4()
        self.correlation_id = correlation_id
        self.sender = {
            "agent_id": sender_id,
            "role": role,
            "authority_level": authority_level
        }
        self.timestamp = timezone.now()
        self.interaction_type = interaction_type
        self.payload = payload
        self.intelligence = {
            "confidence_score": 1.0,
            "reasoning": "",
            "vote": "ABSTAIN"
        }

    def to_dict(self):
        return {
            "header": {
                "message_id": str(self.message_id),
                "correlation_id": str(self.correlation_id),
                "sender": self.sender,
                "timestamp": self.timestamp.isoformat()
            },
            "interaction": {
                "type": self.interaction_type
            },
            "payload": self.payload,
            "intelligence": self.intelligence
        }

class PCABroker:
    """
    Message Broker interno para la coordinación de agentes.
    Valida contratos y persiste interacciones en base de datos.
    """
    def dispatch(self, message: PCAMessage):
        """
        Enruta un mensaje y lo registra de forma persistente.
        """
        AgentInteraction.objects.create(
            id=message.message_id,
            correlation_id=message.correlation_id,
            sender_id=message.sender['agent_id'],
            interaction_type=message.interaction_type,
            payload=message.payload,
            intelligence=message.intelligence
        )

        # En un sistema real, aquí se enviaría a una cola (Redis/RabbitMQ)
        logger.info(f"PCA Broker: Mensaje {message.message_id} persistido y despachado de {message.sender['agent_id']}")
        return True

class ConsensusEngine:
    """
    Motor de Consenso Ponderado.
    Calcula la decisión colectiva basada en autoridad y especialidad.
    """
    def __init__(self):
        # Definición de pesos por especialidad (Mapa conceptual)
        self.authority_weights = {
            3: 1.0, # Soberano
            2: 0.7, # Coordinador
            1: 0.4  # Operativo
        }

    def calculate_consensus(self, votes, intention_domain):
        """
        votes: Lista de diccionarios con {agent_id, authority_level, specialty, vote, confidence}
        intention_domain: El dominio de la intención (ej: 'fiscal', 'comercial')
        """
        if not votes:
            return {"approved": False, "score": 0.0, "reason": "No hay votos disponibles"}

        total_weighted_score = 0.0
        total_weight = 0.0
        veto_active = False

        for v in votes:
            # 1. Peso base por autoridad
            weight = self.authority_weights.get(v['authority_level'], 0.1)

            # 2. Factor de especialidad
            specialty_factor = 1.5 if v['specialty'] == intention_domain else 1.0

            final_weight = weight * specialty_factor

            # 3. Voto numérico
            vote_value = 1.0 if v['vote'] == "APPROVE" else -1.0

            # 4. Verificación de Veto (Nivel 3 en su especialidad)
            if v['authority_level'] == 3 and v['specialty'] == intention_domain and v['vote'] == "REJECT":
                veto_active = True
                logger.warning(f"PCA: VETO detectado por agente {v['agent_id']}")

            total_weighted_score += (vote_value * final_weight * v['confidence'])
            total_weight += final_weight

        if veto_active:
            return {"approved": False, "score": -1.0, "reason": "Veto de autoridad soberana"}

        final_score = total_weighted_score / total_weight if total_weight > 0 else 0.0

        return {
            "approved": final_score > 0.5,
            "score": final_score,
            "reason": "Consenso calculado exitosamente" if final_score > 0.5 else "Consenso insuficiente"
        }

class PCAController:
    """
    Controlador principal del PCA que integra el Broker y el Motor de Consenso.
    """
    def __init__(self):
        self.broker = PCABroker()
        self.consensus_engine = ConsensusEngine()

    def coordinate_intelligence(self, correlation_id, intention, params):
        """
        Simula una ronda de consulta a agentes y devuelve el consenso.
        En producción, esto dispararía tareas asíncronas.
        """
        logger.info(f"PCA: Iniciando coordinación para intención {intention}")

        # Simulación de votos de agentes especializados
        # En el futuro, esto vendrá de los agentes SADI reales
        simulated_votes = [
            {
                "agent_id": "TenienteComercial",
                "authority_level": 1,
                "specialty": "comercial",
                "vote": "APPROVE",
                "confidence": 0.9
            },
            {
                "agent_id": "TenienteRiesgo",
                "authority_level": 2,
                "specialty": "financiero",
                "vote": "APPROVE",
                "confidence": 0.85
            }
        ]

        # Añadir voto de cumplimiento si es una operación sensible
        if params.get('amount', 0) > 1000:
            simulated_votes.append({
                "agent_id": "AgenteCumplimiento",
                "authority_level": 3,
                "specialty": "fiscal",
                "vote": "APPROVE" if params.get('amount', 0) < 5000 else "REJECT",
                "confidence": 1.0
            })

        # Determinar dominio de la intención
        domain = "comercial" # Por defecto para el ejemplo
        if "SALE" in intention or "PAY" in intention:
            domain = "fiscal" if params.get('amount', 0) > 1000 else "comercial"

        consensus = self.consensus_engine.calculate_consensus(simulated_votes, domain)

        # Registrar interacción
        for v in simulated_votes:
            msg = PCAMessage(correlation_id, v['agent_id'], "Agent", v['authority_level'], "QUERY_RESPONSE", v)
            msg.intelligence["vote"] = v['vote']
            msg.intelligence["confidence_score"] = v['confidence']
            self.broker.dispatch(msg)

        return consensus
