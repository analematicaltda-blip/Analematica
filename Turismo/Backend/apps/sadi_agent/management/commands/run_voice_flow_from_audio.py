# backend/apps/sadi_agent/management/commands/run_voice_flow_from_audio.py
import os
import time
import logging
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from apps.sadi_agent.voice_orchestrator import VoiceOrchestrator
from apps.sadi_agent.voice_providers import WhisperProvider, OpenAITTSProvider
from apps.sadi_agent.semantic_engine import SemanticEngine
from apps.sadi_agent.translation_service import TranslationService
from apps.sadi_agent.security import VoiceSecurity
from apps.sadi_agent.semantic_engine import SemanticEngine
from apps.sadi_agent.translation_service import TranslationService
from apps.sadi_agent.security import VoiceSecurity

# Configurar un logger simple para la salida del comando
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Command(BaseCommand):
    help = 'Ejecuta el flujo de voz completo desde un archivo de audio.'

    def add_arguments(self, parser):
        parser.add_argument('audio_input_path', type=str, help='Ruta al archivo de audio de entrada (ej. .wav, .mp3).')
        parser.add_argument('--user', type=str, default='sadi', help='El nombre de usuario para obtener el token de API.')
        parser.add_argument('--output-path', type=str, default='response.mp3', help='Ruta para guardar el archivo de audio de respuesta.')

    def handle(self, *args, **options):
        audio_input_path = Path(options['audio_input_path'])
        output_path = Path(options['output_path'])
        username = options['user']
        User = get_user_model()

        self.stdout.write(self.style.SUCCESS(f"Iniciando flujo de voz completo para el usuario '{username}'..."))
        self.stdout.write(f"Archivo de entrada: '{audio_input_path}'")
        self.stdout.write(f"Archivo de salida: '{output_path}'")

        if not audio_input_path.exists():
            raise CommandError(f"El archivo de entrada '{audio_input_path}' no fue encontrado.")

        try:
            # 1. Obtener el token de API
            user = User.objects.get(username=username)
            token, _ = Token.objects.get_or_create(user=user)
            self.stdout.write("Token de API obtenido con éxito.")

            # 2. Instanciar proveedores reales y el orquestador
            # Las claves de API se toman de las variables de entorno
            stt_provider = WhisperProvider()
            tts_provider = OpenAITTSProvider()
            api_base_url = os.environ.get("SADI_API_BASE_URL", "http://127.0.0.1:8000/api/sarita")

            orchestrator = VoiceOrchestrator(
                api_token=token.key,
                stt_provider=stt_provider,
                tts_provider=tts_provider,
                api_base_url=api_base_url
            )
            self.stdout.write(f"VoiceOrchestrator instanciado con proveedores REALES. Apuntando a: {api_base_url}")

            # 3. Medir latencia y ejecutar el comando de audio
            start_time = time.time()
            self.stdout.write(self.style.NOTICE("\n--- INICIO DEL FLUJO DE VOZ ---"))

            text_response, final_audio_path = orchestrator.handle_audio_command(audio_input_path, output_path)

            end_time = time.time()
            self.stdout.write(self.style.NOTICE("--- FIN DEL FLUJO DE VOZ ---\n"))

            latency = end_time - start_time

            # 4. Mostrar la respuesta y métricas
            self.stdout.write(self.style.SUCCESS("Respuesta de texto final generada:"))
            self.stdout.write(text_response)
            self.stdout.write(self.style.SUCCESS(f"\nRespuesta de audio guardada en: {final_audio_path}"))
            self.stdout.write(self.style.SUCCESS(f"Latencia total del flujo: {latency:.2f} segundos"))

        except User.DoesNotExist:
            raise CommandError(f"El usuario '{username}' no existe.")
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Ha ocurrido un error durante la ejecución: {e}"))
            # Descomentar para un traceback completo si es necesario
            # import traceback
            # traceback.print_exc()
