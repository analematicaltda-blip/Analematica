from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from drf_spectacular.utils import extend_schema
from .semantic_engine import SemanticEngine
from apps.sarita_agents.orchestrator import sarita_orchestrator
import logging

logger = logging.getLogger(__name__)

class MarketingVoiceIntentView(APIView):
    """
    Endpoint para el embudo de marketing conversacional por voz.
    """
    permission_classes = [] # Público para prospectos

    @extend_schema(responses={202: serializers.JSONField()})
    def post(self, request):
        text = request.data.get("text")
        if not text:
            return Response({"error": "No text provided"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Interpretar Intención
        engine = SemanticEngine()
        intent, params, structured_order = engine.interpret(text)

        if not intent or intent.domain.name != 'marketing':
             # Fallback si no detecta marketing explícitamente
             # pero el texto sugiere interés comercial
             pass

        # 2. Activar Agentes de Marketing
        directive = {
            "domain": "marketing",
            "mission": {
                "type": "CONVERSATIONAL_FUNNEL",
                "action": "guide_prospect",
                "entity": "lead"
            },
            "parameters": params or {},
            "voice_context": {
                "original_text": text,
                "actor": "prospect"
            }
        }

        mision = sarita_orchestrator.start_mission(directive)
        sarita_orchestrator.execute_mission(mision.id)

        # Phase 4-M: Respuesta rápida para el flujo conversacional
        # En una implementación real, esperaríamos el reporte de los tenientes
        return Response({
            "intent": intent.name if intent else "explorar_plataforma",
            "confidence": 0.9, # Mock
            "next_action": "qualification",
            "mision_id": mision.id
        }, status=status.HTTP_202_ACCEPTED)
