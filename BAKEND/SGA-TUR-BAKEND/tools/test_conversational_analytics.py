import os
import django
import uuid

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')
django.setup()

from apps.social.models import SocialConversation, SocialMessage
from apps.tourism_intelligence.analytics_engine import ConversationalAnalyticsEngine
from apps.tourism_intelligence.models import ConversationalIntent
from django.contrib.auth import get_user_model

User = get_user_model()

def run_test():
    print("Iniciando prueba de Motor de Analítica Conversacional...")

    # 1. Crear o recuperar usuario turista
    tourist, _ = User.objects.get_or_create(
        username='turista_test',
        defaults={'email': 'turista@test.com', 'role': 'TURIST'} # Nota: corregir a 'TOURIST' si es el valor real del enum
    )

    # 2. Crear una conversación mock
    conv = SocialConversation.objects.create(
        title="Prueba de Inteligencia",
        created_by=tourist
    )

    # 3. Crear mensajes con diferentes intenciones
    messages_data = [
        "Hola, busco un hotel económico en el centro",
        "¿Tienen algún restaurante de comida típica?",
        "Quiero hacer una reserva para mañana a las 8pm",
        "¿Cuál es el precio del tour a la cascada?",
        "¿Cómo puedo llegar al parque principal?",
        "La atención fue pésima, exijo un reclamo",
        "Muchas gracias, excelente servicio"
    ]

    for content in messages_data:
        msg = SocialMessage.objects.create(
            conversation=conv,
            sender=tourist,
            content=content
        )

        # 4. Analizar mensaje
        intent = ConversationalAnalyticsEngine.analyze_message(msg)
        print(f"Mensaje: '{content}' -> Intención Detectada: {intent.intent} (Confianza: {intent.confidence_score}, Sentimiento: {intent.sentiment_score})")

    # 5. Verificar conteo
    count = ConversationalIntent.objects.filter(conversation_id=conv.id).count()
    print(f"\nTotal de intenciones registradas: {count}")

    if count == len(messages_data):
        print("✅ PRUEBA EXITOSA: Todas las intenciones fueron procesadas.")
    else:
        print(f"❌ FALLO: Se esperaban {len(messages_data)} intenciones, se encontraron {count}.")

if __name__ == "__main__":
    run_test()
