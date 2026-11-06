import sys
import re
import json
import subprocess
import os
import tempfile
import glob
from pathlib import Path

# Configuración
OLLAMA_MODEL = "qwen2.5-coder:7b"
BASE_DIR = Path(__file__).parent.parent
TRANSCRIPT_DIR = BASE_DIR / "transcripts"
TRANSCRIPT_DIR.mkdir(exist_ok=True)

# Importamos el transcriptor local
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from local_whisper import transcribe as whisper_transcribe
except ImportError:
    whisper_transcribe = None

def extract_video_id(url):
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/|v\/|shorts\/|youtu.be\/)([0-9A-Za-z_-]{11})',
        r'^([0-9A-Za-z_-]{11})$'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def summarize_locally(text, custom_query=None):
    if custom_query:
        instruction = f"Basándote en la siguiente transcripción, responde a esta duda específica: {custom_query}"
    else:
        instruction = "Genera un resumen estructurado con: 1. TL;DR, 2. Puntos clave y 3. Conclusión."
    
    prompt = f"Eres un asistente experto. {instruction}\n\nTRANSCRIPCIÓN:\n{text[:15000]}"
    
    try:
        cmd = ["ollama", "run", OLLAMA_MODEL, prompt]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', check=True)
        return result.stdout
    except Exception as e:
        return f"Error en Ollama local: {str(e)}"

def process_video(video_id, query=None, only_transcript=False):
    transcript_file = TRANSCRIPT_DIR / f"{video_id}.json"
    
    # 1. ¿Ya tenemos la transcripción guardada?
    if transcript_file.exists():
        print(f"Caché encontrada para {video_id}...", file=sys.stderr)
        with open(transcript_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        # 2. No existe, hay que descargar y transcribir
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        try:
            meta_cmd = ["yt-dlp", "-j", "--skip-download", "--no-playlist", url]
            meta_result = subprocess.run(meta_cmd, capture_output=True, text=True, check=True)
            meta = json.loads(meta_result.stdout)
        except:
            meta = {}

        with tempfile.TemporaryDirectory() as tmpdir:
            audio_output = os.path.join(tmpdir, "audio.%(ext)s")
            cmd = ["yt-dlp", "-f", "ba/b[ext=m4a]/b", "--no-playlist", "--output", audio_output, url]
            
            try:
                print(f"Descargando audio de {video_id}...", file=sys.stderr)
                subprocess.run(cmd, capture_output=True, check=True)
                downloaded_files = glob.glob(os.path.join(tmpdir, "audio.*"))
                
                if downloaded_files:
                    audio_path = downloaded_files[0]
                    print(f"Transcribiendo con Whisper local...", file=sys.stderr)
                    transcript_text = whisper_transcribe(audio_path, language="es")
                    
                    data = {
                        "video_id": video_id,
                        "title": meta.get("title", "Desconocido"),
                        "author": meta.get("uploader", "Desconocido"),
                        "transcript": transcript_text
                    }
                    
                    with open(transcript_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                else:
                    return {"error": "No se pudo descargar el audio."}
            except Exception as e:
                return {"error": f"Error: {str(e)}"}

    # 3. Si solo queremos transcribir, terminamos aquí
    if only_transcript:
        return {
            "title": data["title"],
            "status": "Transcripción guardada localmente",
            "file": str(transcript_file),
            "cached": True if transcript_file.exists() else False
        }

    # 4. Si no, procesamos con Ollama
    print(f"Generando respuesta con Ollama...", file=sys.stderr)
    result_text = summarize_locally(data["transcript"], custom_query=query)
    
    return {
        "title": data["title"],
        "author": data["author"],
        "result": result_text,
        "cached": transcript_file.exists()
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    
    input_str = sys.argv[1]
    video_id = extract_video_id(input_str)
    
    # Flags opcionales
    only_transcript = "--only-transcript" in sys.argv
    query = None
    for arg in sys.argv[2:]:
        if not arg.startswith("--"):
            query = arg
            break
    
    if video_id:
        result = process_video(video_id, query, only_transcript)
        print(json.dumps(result, indent=2, ensure_ascii=False))
