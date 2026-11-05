# backend/apps/sadi_agent/voice_orchestrator.py
import time
import logging
import hashlib
import requests
from pathlib import Path
from django.utils import timezone
from api.models import CustomUser
from .voice_providers import SpeechToTextProvider, TextToSpeechProvider
from .semantic_engine import SemanticEngine
from .translation_service import TranslationService
from .models import VoiceInteractionLog
from apps.admin_plataforma.services.governance_kernel import GovernanceKernel
from apps.finanzas.events import FinancialEventManager, VOICE_SESSION_STARTED, VOICE_MINUTE_CONSUMED

logger = logging.getLogger(__name__)

class VoiceOrchestrator:
    """
    Orquesta el flujo completo de una interacción de voz, aplicando seguridad,
    semántica y auditoría.
    """
    def __init__(self, stt_provider: SpeechToTextProvider, tts_provider: TextToSpeechProvider,
                 semantic_engine: SemanticEngine, translation_service: TranslationService,
                 api_base_url: str = "http://127.0.0.1:8000/api/sarita"):
        self.stt_provider = stt_provider
        self.tts_provider = tts_provider
        self.semantic_engine = semantic_engine
        self.translation_service = translation_service
        self.api_base_url = api_base_url

    def handle_audio_command(self, user: CustomUser, api_token: str, audio_path: Path, output_audio_path: Path) -> (str, Path):
        """
        Flujo principal de la Fase Z para manejar un comando de voz desde audio.
        """
        log = VoiceInteractionLog.objects.create(user=user)
        session_id = str(log.id)

        # Emisión de Evento Financiero (Phase 4-F)
        FinancialEventManager.emit_event(VOICE_SESSION_STARTED, session_id, value=0.0)
        text_response = "Lo siento, ha ocurrido un error inesperado."
        detected_language = "es" # Default

        try:
            # 1. Transcripción y Detección de Idioma
            log.audio_hash = self._calculate_hash(audio_path)
            transcribed_text, detected_language = self.stt_provider.transcribe(audio_path)

            # Cargo por uso de IA (Phase 4-F)
            FinancialEventManager.emit_event(VOICE_MINUTE_CONSUMED, session_id, value=0.05)
            log.transcribed_text = transcribed_text
            log.detected_language = detected_language
            log.save()

            # 2. Normalización a Idioma Base
            normalized_text = self.translation_service.normalize_to_base_language(transcribed_text, detected_language)
            log.normalized_text = normalized_text
            log.save()

            # 3. Interpretación Semántica (Intent Engine)
            intent, entities, structured_order = self.semantic_engine.interpret(normalized_text)
            if not intent:
                raise ValueError("No se pudo interpretar la intención del comando.")
            log.detected_intent = intent
            log.extracted_entities = entities
            # Almacenamos la orden estructurada para el flujo de agentes
            self.current_order = structured_order
            log.save()

            # 4. Verificación de Soberanía y Autoridad (Kernel)
            log.permission_checked = True
            kernel = GovernanceKernel(user=user)

            # El Kernel valida contrato, autoridad y políticas globales
            # Si falla, lanza excepción que atrapamos abajo
            try:
                kernel._validate_authority(kernel._registry[intent.name])
                kernel._evaluate_policies(kernel._registry[intent.name], entities)
                log.permission_granted = True
            except Exception as e:
                log.permission_granted = False
                log.final_status = "REJECTED"
                log.save()
                raise PermissionError(f"Gobernanza bloqueó la acción: {str(e)}")

            log.save()

            # 5. Ejecución Especial o Misión de Agentes
            if intent.name.startswith("STRATEGY_"):
                text_response = self._handle_strategy_voice_command(kernel, intent, entities)
                log.final_status = "COMPLETADA"
            elif intent.name.startswith("OPTIMIZATION_"):
                text_response = self._handle_optimization_voice_command(kernel, intent, entities)
                log.final_status = "COMPLETADA"
            elif intent.name.startswith("AUTONOMY_"):
                text_response = self._handle_autonomy_voice_command(kernel, intent, entities)
                log.final_status = "COMPLETADA"
            elif intent.domain.name == "marketing":
                text_response = self._handle_marketing_voice_command(kernel, intent, entities)
                log.final_status = "COMPLETADA"
            else:
                # Flujo estándar de Misión de Agentes
                directive = self._build_directive(intent, entities)
                mission_id = self._invoke_sarita_api(directive, api_token)
                log.mission_id = mission_id
                log.save()

                final_mission_status = self._poll_mission_status(mission_id, api_token)
                text_response = self._generate_spoken_response(final_mission_status)
                log.final_status = final_mission_status.get("estado", "UNKNOWN")

        except (ValueError, PermissionError) as e:
            text_response = f"Error: {e}"
            log.final_status = "REJECTED"
        except Exception as e:
            logger.error(f"Error inesperado en el flujo de voz: {e}", exc_info=True)
            text_response = "Lo siento, ha ocurrido un error inesperado."
            log.final_status = "FAILED"

        # 6. Traducción y Síntesis de Voz de la Respuesta
        final_response_text = self.translation_service.translate_response(text_response, detected_language)
        log.text_response = final_response_text
        self.tts_provider.speak(final_response_text, output_audio_path)

        log.timestamp_end = timezone.now()
        log.save()

        return final_response_text, output_audio_path

    def _build_directive(self, intent, entities):
        """
        Traductor Voz-a-Agentes: Mapea la orden estructurada a una directiva de misión.
        """
        order = self.current_order
        return {
            "domain": order.get("domain_name", intent.domain.name),
            "mission": {
                "type": order.get("intent_name", intent.name),
                "action": order.get("accion"),
                "entity": order.get("entidad")
            },
            "parameters": order.get("parameters", entities),
            "voice_context": {
                "original_text": order.get("original_text"),
                "actor": order.get("actor", "super_admin")
            }
        }

    def _calculate_hash(self, file_path: Path) -> str:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256.update(byte_block)
        return sha256.hexdigest()

    def _get_headers(self, token: str):
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def _invoke_sarita_api(self, directive: dict, api_token: str) -> str:
        """
        Envía la directiva al endpoint de la API de SARITA.
        """
        url = f"{self.api_base_url}/directive/"
        headers = self._get_headers(api_token)
        logger.debug(f"Invocando API de SARITA en {url} con directiva: {directive}")

        response = requests.post(url, json=directive, headers=headers)

        if response.status_code == 202:
            mission_id = response.json().get("mission_id")
            logger.info(f"API aceptó la directiva. ID de la Misión: {mission_id}")
            return mission_id
        else:
            logger.error(f"Error al invocar la API de SARITA. Status: {response.status_code}, Body: {response.text}")
            raise ConnectionError(f"La API de SARITA devolvió un error: {response.status_code}")

    def _poll_mission_status(self, mission_id: str, api_token: str) -> dict:
        """
        Consulta el estado de la misión hasta que se complete o falle.
        """
        url = f"{self.api_base_url}/missions/{mission_id}/"
        headers = self._get_headers(api_token)
        max_retries = 30
        poll_interval = 2

        for i in range(max_retries):
            logger.debug(f"Polling para misión {mission_id}, intento {i+1}/{max_retries}")
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                status_data = response.json()
                estado = status_data.get("estado")

                if estado in ["EJECUTANDO", "PENDIENTE"]:
                    time.sleep(poll_interval)
                    continue
                else:
                    logger.info(f"Misión {mission_id} alcanzó el estado final: {estado}")
                    return status_data
            else:
                logger.error(f"Error al consultar estado de la misión {mission_id}. Status: {response.status_code}")
                raise ConnectionError(f"Error al consultar el estado de la misión: {response.status_code}")

        raise TimeoutError(f"La misión {mission_id} no finalizó en el tiempo esperado.")

    def _handle_marketing_voice_command(self, kernel: GovernanceKernel, intent, entities) -> str:
        """Maneja el flujo conversacional del embudo de ventas (Fase 4-M)."""
        text = self.current_order.get("original_text", "")
        session_id = str(entities.get("session_id", "default"))

        from apps.sarita_agents.finanzas.capitan_cac import CapitanCAC
        from apps.sarita_agents.finanzas.capitan_ltv import CapitanLTV
        from apps.sarita_agents.finanzas.capitan_roi import CapitanROI
        from apps.finanzas.events import FinancialEventManager, OBJECTION_DETECTED

        # Phase 4-F: Análisis de Rentabilidad en Tiempo Real
        cac_cap = CapitanCAC(coronel=None)
        ltv_cap = CapitanLTV(coronel=None)
        roi_cap = CapitanROI(coronel=None)

        cac = cac_cap.calculate_cac(session_id)
        # Estimación conservadora inicial
        ltv = ltv_cap.estimate_ltv(user_type='prestador', plan_value=20.0)
        roi = roi_cap.evaluate_roi(cac, ltv)

        # Regla Crítica: No vender si CAC > LTV
        if cac > ltv:
            logger.warning(f"MARKETING: CAC ({cac}) excede LTV ({ltv}). Abortando venta proactiva.")
            return "Entiendo tu interés, pero en este momento estamos priorizando perfiles con mayor impacto sistémico. ¿Deseas explorar nuestra documentación?"

        # Retroalimentación: Si ROI es bajo, exploración corta
        if roi < 2.0:
            logger.info(f"MARKETING: ROI bajo ({roi}). Aplicando exploración guiada corta.")

        # Activar el sistema de agentes de marketing
        directive = {
            "domain": "marketing",
            "mission": {
                "type": "CONVERSATIONAL_FUNNEL",
                "action": "guide_prospect",
                "entity": "lead"
            },
            "parameters": entities,
            "voice_context": {
                "original_text": text,
                "actor": "prospect"
            }
        }

        # Iniciamos la misión asíncrona
        from apps.sarita_agents.orchestrator import sarita_orchestrator
        mision = sarita_orchestrator.start_mission(directive)
        sarita_orchestrator.execute_mission(mision.id)

        # Generamos respuesta verbal inmediata basada en la intención
        if intent.name == "explorar_plataforma":
            return "Bienvenido a SARITA. Soy tu asistente comercial. ¿Te interesa vender servicios turísticos o buscas una solución para gobierno?"

        if intent.name == "quiero_vender_turismo":
            return "Excelente. Sarita evita que pierdas dinero por desorden y te organiza las ventas. ¿Trabajas solo o tienes un equipo?"

        if intent.name == "soy_gobierno":
            return "Entendido. Ofrecemos una plataforma integral para secretarías y direcciones de turismo. ¿Deseas ver cómo automatizamos inventarios?"

        if intent.name == "quiero_precio":
            return "Nuestros planes se adaptan a tu tamaño. Primero cuéntame, ¿cuántos servicios gestionas actualmente?"

        return "Entiendo tu interés. Permíteme guiarte para encontrar la mejor solución en Sarita."

    def _handle_optimization_voice_command(self, kernel: GovernanceKernel, intent, entities) -> str:
        """Maneja comandos de voz específicos para la optimización de Fase 6."""
        from apps.ecosystem_optimization.models import OptimizationProposal
        from apps.ecosystem_optimization.services.governance_optimizer import GovernanceOptimizer

        proposal_id = entities.get("proposal_id") or entities.get("id")
        optimizer = GovernanceOptimizer(user=kernel.user)

        if intent.name == "OPTIMIZATION_EXPLAIN":
            proposal = None
            if proposal_id:
                proposal = OptimizationProposal.objects.filter(id=proposal_id).first()
            else:
                proposal = OptimizationProposal.objects.filter(status=OptimizationProposal.Status.PROPOSED).first()

            if not proposal:
                return "El ecosistema está operando de forma óptima. No hay mejoras sugeridas por el momento."

            return f"He detectado un patrón en el dominio {proposal.domain}: {proposal.hallazgo}. Propongo: {proposal.propuesta_ajuste}. ¿Deseas aplicar esta optimización?"

        if intent.name == "OPTIMIZATION_APPROVE":
            if not proposal_id:
                proposal = OptimizationProposal.objects.filter(status=OptimizationProposal.Status.PROPOSED).first()
                if not proposal: return "No hay optimizaciones pendientes."
                proposal_id = proposal.id

            try:
                optimizer.approve_optimization(proposal_id, "Aprobado por voz.")
                optimizer.execute_optimization(proposal_id)
                return "Optimización aplicada correctamente. He ajustado los parámetros del sistema según lo acordado."
            except Exception as e:
                return f"Error al aplicar la optimización: {str(e)}"

        return "Comando de optimización no reconocido."

    def _handle_autonomy_voice_command(self, kernel: GovernanceKernel, intent, entities) -> str:
        """Maneja comandos de voz específicos para la autonomía de Fase F-F."""
        from apps.ecosystem_optimization.models import AutonomousAction, AutonomousExecutionLog, AutonomyControl

        if intent.name == "AUTONOMY_GET_STATUS":
            control = AutonomyControl.objects.filter(domain=None).first()
            enabled = control.is_enabled if control else True
            status = "operativa" if enabled else "bloqueada por Kill Switch"
            count = AutonomousAction.objects.filter(autonomy_level=2).count()
            return f"La autonomía global está actualmente {status}. Tengo {count} acciones tipificadas para ejecución autónoma condicionada."

        if intent.name == "AUTONOMY_KILL_SWITCH":
            domain = entities.get("domain")
            reason = entities.get("reason", "Activación por comando de voz.")
            control, _ = AutonomyControl.objects.get_or_create(domain=domain)
            control.is_enabled = False
            control.reason = reason
            control.updated_by = kernel.user
            control.save()
            return f"Kill Switch activado para {domain or 'todo el sistema'}. He detenido toda ejecución autónoma delegada."

        if intent.name == "AUTONOMY_EXPLAIN_LAST":
            last_log = AutonomousExecutionLog.objects.order_by('-timestamp').first()
            if not last_log:
                return "No se han registrado ejecuciones autónomas recientemente."
            return f"La última acción autónoma fue {last_log.action.name}. Explicación: {last_log.explanation}"

        return "Comando de autonomía no reconocido."

    def _handle_strategy_voice_command(self, kernel: GovernanceKernel, intent, entities) -> str:
        """Maneja comandos de voz específicos para la inteligencia de decisión de Fase 5."""
        from apps.decision_intelligence.models import StrategyProposal

        proposal_id = entities.get("proposal_id") or entities.get("id")

        if intent.name == "STRATEGY_EXPLAIN":
            # Si no hay ID, explicamos la más urgente
            proposal = None
            if proposal_id:
                proposal = StrategyProposal.objects.filter(id=proposal_id).first()
            else:
                proposal = StrategyProposal.objects.filter(status=StrategyProposal.Status.PENDING).order_by('-nivel_urgencia').first()

            if not proposal:
                return "No encontré ninguna propuesta estratégica pendiente de revisión."

            return f"Propuesta de dominio {proposal.domain}. {proposal.contexto_detectado}. Impacto estimado: {proposal.impacto_estimado}. ¿Deseas que la ejecute?"

        if intent.name == "STRATEGY_APPROVE":
            if not proposal_id:
                proposal = StrategyProposal.objects.filter(status=StrategyProposal.Status.PENDING).order_by('-nivel_urgencia').first()
                if not proposal: return "No hay propuestas pendientes para aprobar."
                proposal_id = proposal.id

            try:
                proposal = StrategyProposal.objects.get(id=proposal_id)
                proposal.status = StrategyProposal.Status.APPROVED
                proposal.save()

                result = kernel.execute_strategic_proposal(proposal_id)
                return f"Propuesta aprobada y ejecutada correctamente. {result.get('message', '')}"
            except Exception as e:
                return f"No se pudo ejecutar la propuesta: {str(e)}"

        if intent.name == "STRATEGY_REJECT":
            if not proposal_id: return "Por favor, especifica qué propuesta deseas rechazar."
            StrategyProposal.objects.filter(id=proposal_id).update(status=StrategyProposal.Status.REJECTED)
            return "Propuesta rechazada y archivada."

        return "Comando de estrategia no reconocido."

    def _generate_spoken_response(self, mission_status: dict) -> str:
        """
        Voice Feedback Loop: Utiliza el LLM para generar una respuesta natural
        basada en el resultado técnico del agente.
        """
        if not self.semantic_engine.llm:
            # Fallback a respuesta estática si no hay LLM
            estado = mission_status.get("estado")
            if estado == "COMPLETADA": return "Operación finalizada correctamente."
            return f"La operación terminó con estado: {estado}"

        prompt = f"""
        Como SARITA, genera una respuesta verbal breve y profesional para el Super Administrador.

        RESULTADO TÉCNICO DE LA MISIÓN:
        {json.dumps(mission_status, indent=2)}

        REGLAS:
        1. Sé concisa y directa.
        2. Confirma si la acción fue exitosa o explica el error.
        3. Usa un tono de asistente ejecutivo.
        4. No menciones IDs técnicos ni JSON.
        """

        try:
            from langchain_core.messages import SystemMessage
            response = self.semantic_engine.llm.invoke([SystemMessage(content=prompt)])
            return response.content
        except Exception as e:
            logger.error(f"Error generando respuesta verbal con LLM: {e}")
            return "Operación procesada. Revise el panel para más detalles."
