from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.parsers import MultiPartParser
from drf_spectacular.utils import extend_schema
from pathlib import Path
from django.conf import settings
from .voice_orchestrator import VoiceOrchestrator
from .voice_providers import WhisperProvider, OpenAITTSProvider
from .semantic_engine import SemanticEngine
from .translation_service import TranslationService
from api.models import CustomUser

class MarketingVoiceAudioView(APIView):
    """
    Endpoint para recibir audio directo del embudo de marketing.
    """
    permission_classes = []
    parser_classes = [MultiPartParser]

    @extend_schema(responses={200: serializers.JSONField()})
    def post(self, request):
        audio_file = request.FILES.get("audio")
        if not audio_file:
            return Response({"error": "No audio provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Guardar audio temporal
        temp_dir = Path(settings.MEDIA_ROOT) / "temp_audio"
        temp_dir.mkdir(parents=True, exist_ok=True)
        audio_path = temp_dir / audio_file.name
        with open(audio_path, 'wb+') as destination:
            for chunk in audio_file.chunks():
                destination.write(chunk)

        output_audio_path = temp_dir / f"response_{audio_file.name}"

        # Orquestación
        orchestrator = VoiceOrchestrator(
            stt_provider=WhisperProvider(),
            tts_provider=OpenAITTSProvider(),
            semantic_engine=SemanticEngine(),
            translation_service=TranslationService()
        )

        # Usar usuario anónimo o sistema para el funnel
        # Intentamos obtener un usuario lead o simplemente pasar None si el orquestador lo soporta
        # Por simplicidad en Phase 4-M, buscamos el superadmin como 'actor' de respaldo
        admin_user = CustomUser.objects.filter(is_superuser=True).first()

        try:
            # mock token for internal call
            token = "mock_token"
            text_response, audio_response_path = orchestrator.handle_audio_command(
                user=admin_user,
                api_token=token,
                audio_path=audio_path,
                output_audio_path=output_audio_path
            )

            # Devolver URL del audio de respuesta
            relative_path = audio_response_path.relative_to(settings.MEDIA_ROOT)
            return Response({
                "text": text_response,
                "audio_url": f"{settings.MEDIA_URL}{relative_path}"
            })

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
