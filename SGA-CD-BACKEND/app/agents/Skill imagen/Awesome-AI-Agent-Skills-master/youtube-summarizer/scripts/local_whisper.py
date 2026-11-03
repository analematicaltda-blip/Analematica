import os
import sys
from pathlib import Path

# Configuraciones extraídas de tu telegram_bridge.py
WHISPER_MODEL = "tiny"
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE_TYPE = "int8"
WHISPER_DOWNLOAD_ROOT = "D:/IA/CODE/claudebot/models_stt/whisper"

def transcribe(audio_path, language="es"):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return "Error: faster-whisper no está instalado."

    if not os.path.exists(audio_path):
        return f"Error: Archivo no encontrado en {audio_path}"

    model = WhisperModel(
        WHISPER_MODEL,
        device=WHISPER_DEVICE,
        compute_type=WHISPER_COMPUTE_TYPE,
        download_root=WHISPER_DOWNLOAD_ROOT
    )

    segments, info = model.transcribe(audio_path, beam_size=1, language=language if language != "auto" else None)
    
    text = ""
    for segment in segments:
        text += segment.text + " "
    
    return text.strip()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python local_whisper.py <audio_path> [lang]")
        sys.exit(1)
    
    path = sys.argv[1]
    lang = sys.argv[2] if len(sys.argv) > 2 else "es"
    print(transcribe(path, lang))
