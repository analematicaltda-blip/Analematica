# backend/apps/sadi_agent/management/commands/run_voice_command.py
import os
import logging
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from apps.sadi_agent.voice_orchestrator import VoiceOrchestrator
from apps.sadi_agent.voice_providers import SpeechToTextProvider, TextToSpeechProvider

# --- Proveedores Dummy para Pruebas Basadas en Texto ---

class DummySttProvider(SpeechToTextProvider):
    """Proveedor STT que no hace nada, para pruebas de texto."""
    def transcribe(self, audio_path: Path) -> str:
        # En una prueba de texto, la transcripción no se invoca.
        # Se podría devolver el contenido del archivo si fuera un archivo de texto.
        logging.warning("Se ha llamado a DummySttProvider.transcribe, lo cual es inesperado en una prueba de texto.")
        return ""

class DummyTtsProvider(TextToSpeechProvider):
    """Proveedor TTS que no hace nada, solo registra el texto que recibiría."""
    def speak(self, text: str, output_path: Path):
        logging.info(f"[DUMMY TTS] Recibido para hablar: '{text}'. No se generará archivo de audio.")
        # No se realiza ninguna acción, ya que es una simulación de texto.
        pass

# Configurar un logger simple para la salida del comando
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Command(BaseCommand):
    help = 'Simula la ejecución de un comando de voz basado en TEXTO a través del VoiceOrchestrator.'

    def add_arguments(self, parser):
        parser.add_argument('command_text', type=str, help='El texto del comando a simular.')
        parser.add_argument('--user', type=str, default='sadi', help='El nombre de usuario para obtener el token de API.')

    def handle(self, *args, **options):
        command_text = options['command_text']
        username = options['user']
        User = get_user_model()

        self.stdout.write(self.style.SUCCESS(f"Iniciando simulación de comando de texto para el usuario '{username}'..."))
        self.stdout.write(f"Comando: '{command_text}'")

        try:
            # 1. Obtener el token de API
            user = User.objects.get(username=username)
            token, _ = Token.objects.get_or_create(user=user)
            self.stdout.write("Token de API obtenido con éxito.")

            # 2. Instanciar proveedores dummy y el orquestador
            stt_dummy = DummySttProvider()
            tts_dummy = DummyTtsProvider()
            api_base_url = os.environ.get("SADI_API_BASE_URL", "http://127.0.0.1:8000/api/sarita")

            orchestrator = VoiceOrchestrator(
                api_token=token.key,
                stt_provider=stt_dummy,
                tts_provider=tts_dummy,
                api_base_url=api_base_url
            )
            self.stdout.write(f"VoiceOrchestrator instanciado con proveedores DUMMY. Apuntando a: {api_base_url}")

            # 3. Ejecutar el comando de texto
            self.stdout.write(self.style.NOTICE("\n--- INICIO DE LA ORQUESTACIÓN DE TEXTO ---"))
            text_response = orchestrator.handle_text_command(command_text)
            self.stdout.write(self.style.NOTICE("--- FIN DE LA ORQUESTACIÓN DE TEXTO ---\n"))

            # 4. Mostrar la respuesta final
            self.stdout.write(self.style.SUCCESS("Respuesta de texto final generada:"))
            self.stdout.write(text_response)

        except User.DoesNotExist:
            raise CommandError(f"El usuario '{username}' no existe.")
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Ha ocurrido un error durante la ejecución: {e}"))
            # Opcional: imprimir traceback si se necesita más detalle en el debug
            # import traceback
            # traceback.print_exc()
