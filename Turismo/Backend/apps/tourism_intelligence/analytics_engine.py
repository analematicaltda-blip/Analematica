import logging
import re
from .models import ConversationalIntent, ConversationalKPI
from apps.social.models import SocialMessage, SocialConversation
from django.utils import timezone
from django.db.models import Avg, Count, F
from datetime import timedelta

logger = logging.getLogger(__name__)

class ConversationalAnalyticsEngine:
    """
    Motor de análisis de conversaciones para Vía 3 (Turistas).
    Analiza mensajes de SocialMessage y extrae intenciones y KPIs con lógica refinada.
    """

    INTENT_KEYWORDS = {
        ConversationalIntent.IntentType.SEARCH_HOTEL: [
            r"hotel", r"hospedaje", r"dormir", r"alojamiento", r"cama", r"estadía", r"hostal", r"posada",
            r"habitación", r"cuarto", r"piso", r"apartamento", r"airbnb", r"donde quedarme"
        ],
        ConversationalIntent.IntentType.SEARCH_FOOD: [
            r"comer", r"restaurante", r"hambre", r"cena", r"almuerzo", r"desayuno", r"comida", r"gastronomía",
            r"plato", r"menú", r"carta", r"café", r"panadería", r"antojo", r"típico"
        ],
        ConversationalIntent.IntentType.BOOKING_REQUEST: [
            r"reservar", r"reserva", r"cupo", r"disponibilidad", r"separar", r"agendar", r"cita", r"confirmar"
        ],
        ConversationalIntent.IntentType.PRICING_QUERY: [
            r"precio", r"cuánto", r"costo", r"valor", r"tarifa", r"vale", r"barato", r"caro", r"descuento",
            r"promoción", r"presupuesto", r"cotización"
        ],
        ConversationalIntent.IntentType.HOW_TO_ARRIVE: [
            r"llegar", r"ubicación", r"gps", r"mapa", r"dirección", r"queda", r"lejos", r"cerca", r"transporte",
            r"bus", r"taxi", r"carro", r"vía", r"carretera", r"parqueadero"
        ],
        ConversationalIntent.IntentType.SERVICE_COMPLAINT: [
            r"queja", r"reclamo", r"malo", r"pésimo", r"sucio", r"demora", r"caro", r"estafa", r"problema",
            r"incumplimiento", r"decepción", r"asco", r"no sirve", r"devuélvame", r"estafado"
        ],
        ConversationalIntent.IntentType.POSITIVE_FEEDBACK: [
            r"gracias", r"excelente", r"bueno", r"perfecto", r"recomiendo", r"maravilloso", r"lindo",
            r"bonito", r"amable", r"top", r"genial", r"bacano", r"chévere", r"super", r"recomiendo"
        ]
    }

    @staticmethod
    def analyze_message(message: SocialMessage):
        """
        Analiza un mensaje individual y registra la intención con puntuación de confianza y sentimiento.
        """
        content = message.content.lower()
        detected_intent = ConversationalIntent.IntentType.POSITIVE_FEEDBACK
        max_matches = 0
        confidence = 0.5
        sentiment = 0.0
        entities = {}

        # 1. Detección de Intención basada en Regex (Refinada)
        for intent, patterns in ConversationalAnalyticsEngine.INTENT_KEYWORDS.items():
            matches = sum(1 for pattern in patterns if re.search(pattern, content))
            if matches > max_matches:
                max_matches = matches
                detected_intent = intent

        if max_matches > 0:
            confidence = min(0.5 + (max_matches * 0.1), 0.95)

        # 2. Análisis de Sentimiento (Refinado con Intensidad)
        positive_words = ["gracias", "excelente", "bueno", "perfecto", "maravilloso", "amable", "lindo", "genial", "chévere", "recomiendo"]
        negative_words = ["queja", "reclamo", "malo", "pésimo", "sucio", "estafa", "problema", "horrible", "asco", "pobre"]
        intensity_modifiers = ["muy", "bastante", "extremadamente", "demasiado", "increíblemente"]

        pos_score = 0
        neg_score = 0

        words = content.split()
        for i, word in enumerate(words):
            clean_word = re.sub(r'[^\w\s]', '', word)
            multiplier = 1.5 if i > 0 and words[i-1] in intensity_modifiers else 1.0
            if clean_word in positive_words:
                pos_score += (1 * multiplier)
            if clean_word in negative_words:
                neg_score += (1 * multiplier)

        if pos_score + neg_score > 0:
            sentiment = (pos_score - neg_score) / (pos_score + neg_score)

        # 3. Extracción de Entidades (Mejorada)
        if detected_intent == ConversationalIntent.IntentType.SEARCH_HOTEL:
            entities["category"] = "ACCOMMODATION"
        elif detected_intent == ConversationalIntent.IntentType.SEARCH_FOOD:
            entities["category"] = "RESTAURANT"

        # Búsqueda de posibles menciones de dinero
        money = re.search(r"(\d+([\.,]\d+)?)", content)
        if money:
            entities["price_mentioned"] = money.group(1)

        # 4. Persistir el análisis
        intent_obj, created = ConversationalIntent.objects.update_or_create(
            message_id=message.id,
            defaults={
                'conversation_id': message.conversation_id,
                'tourist': message.sender,
                'intent': detected_intent,
                'confidence_score': confidence,
                'sentiment_score': sentiment,
                'detected_entities': entities
            }
        )

        # 5. Integración Vía 4: Disparar automatización económica
        try:
            from apps.turismo.services.economic_automation import EconomicAutomationService
            EconomicAutomationService.process_intent_for_automation(intent_obj)
        except Exception as e:
            logger.error(f"Vía 4: Error en automatización económica: {e}")

        return intent_obj

    @staticmethod
    def update_provider_kpis(provider):
        """
        Calcula KPIs reales de respuesta para un prestador.
        Analiza el tiempo entre mensajes de turistas y las respuestas del dueño del negocio.
        """
        now = timezone.now()
        period = now.strftime("%Y-%m")
        owner = provider.owner

        # Buscar todas las conversaciones donde el dueño es participante
        conversations = SocialConversation.objects.filter(memberships__user=owner)

        delays = []
        for conv in conversations:
            messages = conv.messages.all().order_by('created_at')
            last_tourist_msg_time = None

            for msg in messages:
                # Si el mensaje es de un turista (no es el dueño y no es staff)
                if msg.sender != owner and msg.sender.role == 'TOURIST':
                    last_tourist_msg_time = msg.created_at
                # Si el mensaje es la respuesta del dueño tras un mensaje de turista
                elif msg.sender == owner and last_tourist_msg_time:
                    delay = (msg.created_at - last_tourist_msg_time).total_seconds()
                    delays.append(delay)
                    last_tourist_msg_time = None # Reset para esperar el siguiente par

        avg_time = sum(delays) / len(delays) if delays else 0.0
        total_chats = len(delays) # Estimación simplificada de interacciones completadas

        kpi, created = ConversationalKPI.objects.update_or_create(
            provider=provider,
            period=period,
            defaults={
                'avg_response_time_seconds': avg_time,
                'response_rate': 1.0 if total_chats > 0 else 0.0,
                'total_chats': total_chats,
                'missed_chats': 0
            }
        )
        return kpi
