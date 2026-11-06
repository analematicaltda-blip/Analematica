# backend/apps/sadi_agent/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MarketingVoiceIntentView
from .views_voice import MarketingVoiceAudioView

app_name = 'sadi_agent'

# El router para el ViewSet de AgentExecution
router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('intent/', MarketingVoiceIntentView.as_view(), name='marketing-intent-base'),
    path('v1/marketing/intent/', MarketingVoiceIntentView.as_view(), name='marketing-intent'),
    path('v1/marketing/audio/', MarketingVoiceAudioView.as_view(), name='marketing-audio'),
]
