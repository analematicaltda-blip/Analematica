import sys
import re
import json
import os
import subprocess
from pathlib import Path

# Configuración
OLLAMA_MODEL = "llama3.2:3b"
BASE_DIR = Path(__file__).parent.parent
TRANSCRIPT_DIR = BASE_DIR / "transcripts"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
SUMMARIZER_SCRIPT = Path(__file__).parent / "summarizer.py"

def clean_ansi(text):
    """Elimina códigos de escape de terminal (p[1D[K, etc) y limpia el texto."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    text = ansi_escape.sub('', text)
    # También eliminamos secuencias específicas de Ollama que a veces se filtran
    text = re.sub(r'\[\d+D', '', text)
    text = re.sub(r'\[\d+K', '', text)
    return text.strip()

def call_ollama(prompt):
    try:
        # Usamos env con PYTHONIOENCODING para asegurar UTF-8
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        cmd = ["ollama", "run", OLLAMA_MODEL, prompt]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', check=True, env=env)
        return clean_ansi(result.stdout)
    except Exception as e:
        return f"Error en Ollama: {str(e)}"

def generate_mega_script(video_ids, instruction):
    final_script_path = OUTPUT_DIR / "guion_final_sin_duplicados.txt"
    all_pepas = []
    
    # 1. EXTRACCIÓN Y LIMPIEZA DE PUNTOS CLAVE
    for i, vid in enumerate(video_ids):
        transcript_file = TRANSCRIPT_DIR / f"{vid}.json"
        if not transcript_file.exists():
            print(f"[{i+1}/{len(video_ids)}] Transcribiendo {vid}...", file=sys.stderr)
            subprocess.run([sys.executable, str(SUMMARIZER_SCRIPT), vid, "--only-transcript"], check=True)
        
        with open(transcript_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"[{i+1}/{len(video_ids)}] Analizando: {data['title']}...", file=sys.stderr)
            pepas_prompt = f"Analiza esta transcripción y extrae los 10 puntos técnicos más importantes. Evita generalidades, ve al grano:\n\n{data['transcript'][:15000]}"
            pepas = call_ollama(pepas_prompt)
            all_pepas.append(f"FUENTE: {data['title']}\n{pepas}")

    # 2. PASADA DE DE-DUPLICACIÓN (Fusionar conocimientos)
    print("Fusionando información y eliminando repetidos...", file=sys.stderr)
    fusion_prompt = f"""
    Actúa como un Editor Jefe. Tienes varios análisis de videos sobre el mismo tema. 
    TU MISIÓN: 
    1. Identifica los temas que se repiten en las fuentes.
    2. Crea una LISTA MAESTRA de puntos clave ÚNICOS y PROFUNDOS.
    3. Si dos fuentes hablan de lo mismo, combina la información para que sea la más completa posible.
    4. Elimina cualquier redundancia.
    
    DATOS DE ENTRADA:
    {" ".join(all_pepas)}
    """
    master_insights = call_ollama(fusion_prompt)

    # 3. REDACCIÓN DEL GUION BASADO EN LA LISTA MAESTRA ÚNICA
    print("Redactando guion final consolidado (Larga Duración)...", file=sys.stderr)
    
    # Dividimos la redacción en 3 bloques para mantener el largo sin resumir
    script_parts = []
    
    # Intro
    script_parts.append(call_ollama(f"Escribe una INTRODUCCIÓN ÉPICA y LARGA (400 palabras) para: {instruction}"))
    
    # Cuerpo (dividido en dos para asegurar longitud)
    script_parts.append(call_ollama(f"Redacta la PRIMERA PARTE del guion detallando a fondo estos puntos (mínimo 1000 palabras):\n{master_insights[:len(master_insights)//2]}"))
    script_parts.append(call_ollama(f"Redacta la SEGUNDA PARTE del guion detallando a fondo el resto de puntos (mínimo 1000 palabras):\n{master_insights[len(master_insights)//2:]}"))
    
    # Outro
    script_parts.append(call_ollama(f"Escribe una CONCLUSIÓN potente para este video."))

    # Guardado Final con Codificación Correcta
    final_content = "\n\n".join(script_parts)
    with open(final_script_path, 'w', encoding='utf-8') as f:
        f.write(final_content)

    return f"Guion consolidado y sin duplicados guardado en: {final_script_path}"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(1)
    
    args = sys.argv[1:]
    mode = "mega" if args[0] == "--mode" and args[1] == "mega" else "summary"
    if args[0] == "--mode": args = args[2:]
    
    instruction = args[0]
    ids = args[1:]
    
    result = generate_mega_script(ids, instruction)
    print(result)
