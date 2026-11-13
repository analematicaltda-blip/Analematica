import os
import subprocess
import asyncio

SCRIPT_PAISA = (
    "¡Qué más, pues! En Colombia sabemos que el talento no se improvisa: se forja con disciplina, sudor y berraquera cada día en la cancha y en la tarima. "
    "Pero seamos sinceros: llevar una academia con planillas de papel, notas perdidas y chats interminables, le quita tiempo a lo que de verdad importa: formar campeones y artistas. "
    "Por eso creamos SGA-CD: la plataforma integral que conecta a entrenadores, docentes, directores y familias en un solo lugar. Asistencia georreferenciada al instante, "
    "carnets digitales que tus alumnos llevan con orgullo en el móvil, y seguimiento técnico paso a paso. "
    "Ya sea que lideres una escuela de fútbol, una academia de patinaje, un conservatorio de música o un colegio completo: aquí la tecnología trabaja para potenciar el talento de tu gente. "
    "Lleva tu institución al nivel que se merece con SGA-CD y siente la tranquilidad de tener el control en la palma de tu mano. Conócenos hoy mismo."
)

async def generar_locucion():
    print("-> Generando locución neuronal colombiana (Acento Paisa con Edge-TTS)...")
    # Genera la locución con es-CO-GonzaloNeural con ritmo continuo sin pausas muertas
    cmd = [
        "edge-tts",
        "--voice", "es-CO-GonzaloNeural",
        "--rate=+6%",
        "--pitch=+0Hz",
        "--text", SCRIPT_PAISA,
        "--write-media", "/app/output/locucion_paisa.mp3"
    ]
    proc = await asyncio.create_subprocess_exec(*cmd)
    await proc.communicate()
    print("-> Locución generada exitosamente: /app/output/locucion_paisa.mp3")

def renderizar_videos():
    os.makedirs("/app/output", exist_ok=True)
    asyncio.run(generar_locucion())
    
    # 1. Video Horizontal 16:9 (1920x1080) para Canal YouTube Principal
    print("-> Renderizando Video Horizontal 16:9 (1920x1080)...")
    cmd_16_9 = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=#070b14:s=1920x1080:d=45",
        "-i", "/app/output/locucion_paisa.mp3",
        "-filter_complex",
        "[0:v]drawtext=text='SGA-CD':fontcolor=#38bdf8:fontsize=72:x=(w-text_w)/2:y=(h-text_h)/2-120,"
        "drawtext=text='Gestion Deportiva y Cultural de Colombia':fontcolor=#f8fafc:fontsize=42:x=(w-text_w)/2:y=(h-text_h)/2-30,"
        "drawtext=text='Tecnologia de Vanguardia para Clubes y Academias':fontcolor=#4ade80:fontsize=32:x=(w-text_w)/2:y=(h-text_h)/2+50[v]",
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p", "-shortest",
        "/app/output/sga_promo_youtube_16_9.mp4"
    ]
    subprocess.run(cmd_16_9, check=True)
    print("-> Video 16:9 completado: /app/output/sga_promo_youtube_16_9.mp4")

    # 2. Video Vertical 9:16 (1080x1920) para YouTube Shorts, Reels y TikTok
    print("-> Renderizando Video Vertical 9:16 (1080x1920) para Shorts/TikTok...")
    cmd_9_16 = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=#0f172a:s=1080x1920:d=45",
        "-i", "/app/output/locucion_paisa.mp3",
        "-filter_complex",
        "[0:v]drawtext=text='SGA-CD':fontcolor=#38bdf8:fontsize=84:x=(w-text_w)/2:y=(h-text_h)/2-200,"
        "drawtext=text='Formando Campeones':fontcolor=#f8fafc:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2-100,"
        "drawtext=text='y Artistas en Colombia':fontcolor=#4ade80:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2-30,"
        "drawtext=text='Control Total en el Movil':fontcolor=#cbd5e1:fontsize=36:x=(w-text_w)/2:y=(h-text_h)/2+70[v]",
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p", "-shortest",
        "/app/output/sga_promo_shorts_9_16.mp4"
    ]
    subprocess.run(cmd_9_16, check=True)
    print("-> Video 9:16 completado: /app/output/sga_promo_shorts_9_16.mp4")

if __name__ == '__main__':
    renderizar_videos()