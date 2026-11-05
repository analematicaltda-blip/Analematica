# backend/apps/sadi_agent/semantic_engine.py
import logging
import json
import os
from typing import Tuple, Dict, Optional
from django.conf import settings
from .models import Intent, SemanticDomain
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)

class SemanticEngine:
    """
    Motor Semántico basado en LLM para interpretar intenciones y extraer parámetros.
    Reemplaza al motor antiguo basado en Regex.
    """

    def __init__(self, model_name: str = "gpt-4o"):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
             logger.warning("OPENAI_API_KEY no configurada. El motor semántico operará en modo degradado/mock.")
             self.llm = None
        else:
            self.llm = ChatOpenAI(
                model=model_name,
                openai_api_key=self.api_key,
                temperature=0
            )

    def interpret(self, text: str) -> Tuple[Optional[Intent], Dict, Dict]:
        """
        Interpreta el texto usando un LLM para encontrar la intención y extraer entidades.
        Devuelve (Objeto Intent, Parámetros, Orden Completa JSON).
        """
        logger.info(f"INTERPRETANDO (LLM): '{text}'")

        if not self.api_key:
            intent, params = self._mock_interpret(text)
            return intent, params, {}

        # Obtener catálogo de intenciones disponibles para el prompt
        intents_catalog = self._get_intents_catalog()

        system_prompt = f"""
        Eres el Motor de Intenciones de SARITA (Intent Engine). Tu tarea es convertir comandos de voz o texto en lenguaje natural
        a órdenes estructuradas JSON para el Sistema Operativo Empresarial.

        CATÁLOGO DE INTENCIONES SISTÉMICAS:
        {json.dumps(intents_catalog, indent=2)}

        REGLAS DE INTERPRETACIÓN (Fase 6: Inteligencia Operativa):
        1. Identifica el DOMINIO (comercial, contable, operativo, financiero, archivistico, nomina).
        2. Determina el TIPO DE ACCIÓN (consultar, crear, modificar, aprobar, eliminar).
        3. Identifica la ENTIDAD afectada (venta, gasto, pago, nomina, saldo, etc.).
        4. Para Gastos/Pagos, identifica montos y cuentas si se mencionan (ej. 110505 para Caja).
        5. Extrae todos los PARÁMETROS necesarios del contexto verbal.
        6. Devuelve ÚNICAMENTE un objeto JSON con la siguiente estructura:
           {{
             "actor": "user_agent",
             "domain_name": "nombre_del_dominio",
             "intent_name": "NOMBRE_DE_LA_INTENCION",
             "accion": "tipo_de_accion",
             "entidad": "nombre_de_la_entidad",
             "parameters": {{ "llave": "valor" }},
             "thought": "Breve explicación de por qué elegiste esta intención"
           }}
        6. Si el comando es ambiguo o no reconocido, devuelve {{"error": "UNKNOWN_INTENT"}}.

        EJEMPLO:
        Entrada: "Sarita, crea un nuevo comprobante contable por dos millones y medio por concepto de pago a proveedor"
        Salida: {{
          "actor": "super_admin",
          "domain_name": "contable",
          "intent_name": "ERP_CREATE_VOUCHER",
          "accion": "crear",
          "entidad": "comprobante",
          "parameters": {{
            "valor": 2500000,
            "concepto": "pago proveedor"
          }}
        }}
        """

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=text)
            ]

            response = self.llm.invoke(messages)
            result = json.loads(response.content)

            if "error" in result:
                logger.warning(f"LLM no pudo interpretar el comando: {result['error']}")
                return None, {}

            # Buscar el objeto Intent en la base de datos
            intent = Intent.objects.filter(
                name=result["intent_name"],
                domain__name=result["domain_name"]
            ).first()

            if not intent:
                logger.error(f"LLM sugirió intención '{result['intent_name']}' pero no existe en BD.")
                return None, {}

            logger.info(f"INTENCIÓN DETECTADA: {intent.name}")
            return intent, result.get("parameters", {}), result

        except Exception as e:
            logger.error(f"Error en interpretación LLM: {e}", exc_info=True)
            return None, {}, {}

    def _get_intents_catalog(self) -> list:
        """Genera una lista de diccionarios con las intenciones y sus descripciones."""
        catalog = []
        for intent in Intent.objects.select_related('domain').all():
            catalog.append({
                "intent": intent.name,
                "domain": intent.domain.name,
                "description": intent.description
            })
        return catalog

    def _mock_interpret(self, text: str) -> Tuple[Optional[Intent], Dict]:
        """Fallback para cuando no hay API Key o para pruebas rápidas."""
        text_lower = text.lower()
        if "registra" in text_lower or "alta" in text_lower:
            intent = Intent.objects.filter(name='ONBOARDING_PRESTADOR').first()
            return intent, {"nombre_comercial": "Prestador Mock", "email": "mock@sarita.com"}
        return None, {}
