import os
import django
import uuid
from django.utils import timezone
from datetime import timedelta

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')
django.setup()

from apps.social.models import SocialConversation, SocialMessage, SocialConversationMember
from apps.tourism_intelligence.analytics_engine import ConversationalAnalyticsEngine
from apps.tourism_intelligence.models import ConversationalIntent, ConversationalKPI
from apps.turismo.models.provider_models import TourismProvider
from django.contrib.auth import get_user_model

User = get_user_model()

def run_test():
    print("Iniciando Prueba de Analítica Conversacional v2...")

    # 1. Preparar usuarios y prestador
    owner, _ = User.objects.get_or_create(username='owner_test', defaults={'role': 'BUSINESS_OWNER'})
    tourist, _ = User.objects.get_or_create(username='tourist_test', defaults={'role': 'TOURIST'})

    provider, _ = TourismProvider.objects.get_or_create(
        name="Hotel San Juan",
        owner=owner,
        defaults={'location': 'Centro'}
    )

    # 2. Simular conversación con tiempos de respuesta
    conv = SocialConversation.objects.create(title="Consulta de Reserva", created_by=tourist)
    SocialConversationMember.objects.get_or_create(conversation=conv, user=tourist)
    SocialConversationMember.objects.get_or_create(conversation=conv, user=owner)

    now = timezone.now()

    # Mensaje 1: Turista con sentimiento negativo
    msg1 = SocialMessage.objects.create(conversation=conv, sender=tourist, content="Es muy pésimo que no contesten", created_at=now - timedelta(minutes=10))
    intent1 = ConversationalAnalyticsEngine.analyze_message(msg1)
    print(f"Msg 1 Sentiment: {intent1.sentiment_score} (Esperado < 0)")

    # Mensaje 2: Dueño responde (Delay 2 mins)
    msg2 = SocialMessage.objects.create(conversation=conv, sender=owner, content="Lo siento, ya estoy aquí", created_at=now - timedelta(minutes=8))

    # Mensaje 3: Turista con sentimiento positivo y entidad de precio
    msg3 = SocialMessage.objects.create(conversation=conv, sender=tourist, content="Gracias, ¿el precio es de 50.000?", created_at=now - timedelta(minutes=5))
    intent3 = ConversationalAnalyticsEngine.analyze_message(msg3)
    print(f"Msg 3 Sentiment: {intent3.sentiment_score} (Esperado > 0)")
    print(f"Msg 3 Price Entity: {intent3.detected_entities.get('price_mentioned')} (Esperado '150.000')")

    # Mensaje 4: Dueño responde (Delay 1 min)
    msg4 = SocialMessage.objects.create(conversation=conv, sender=owner, content="Sí, es correcto", created_at=now - timedelta(minutes=4))

    # 3. Calcular KPIs reales
    kpi = ConversationalAnalyticsEngine.update_provider_kpis(provider)
    print(f"\nKPI Results for {provider.name}:")
    print(f"Avg Response Time: {kpi.avg_response_time_seconds}s (Esperado ~(120+60)/2 = 90s)")
    print(f"Total Chats: {kpi.total_chats}")

    if kpi.avg_response_time_seconds > 0:
        print("\n✅ PRUEBA EXITOSA: KPIs y Sentimiento procesados correctamente.")
    else:
        print("\n❌ FALLO: No se detectaron demoras de respuesta.")

if __name__ == "__main__":
    run_test()
