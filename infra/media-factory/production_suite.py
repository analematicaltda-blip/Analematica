import os
import subprocess
import asyncio

# 1. Guión Maestro 5 Minutos (Español Colombiano - Cadencia Paisa, Cero Silencios, Cero Precios)
GUION_5_MINUTOS = (
    "¡Qué más, pues! En Antioquia y en cada rincón de Colombia sabemos que el talento no se improvisa: se forja con disciplina, sudor y berraquera cada bendito día en la cancha, en la pista y en la tarima. "
    "Desde el pelao que sueña con meter un gol en el Atanasio, hasta la niña que deja el alma en los patines o el joven que afina su violín para tocar en el teatro más grande del país. "
    "Pero seamos muy sinceros: dirigir una academia, un club deportivo o una institución cultural no es tarea fácil. Cuántas horas no se pierden lidiando con planillas de papel que se mojan con la lluvia, "
    "chats de WhatsApp que colapsan a medianoche con preguntas de los acudientes, y reportes que nunca cuadran cuando llega el momento de rendir cuentas. "
    "Ese desorden administrativo le quita tiempo y energía a lo que de verdad tiene valor: formar campeones, inspirar artistas y transformar vidas. "
    "Por eso diseñamos SGA-CD: la plataforma integral pensada por y para nuestras instituciones colombianas. Un ecosistema tecnológico robusto donde entrenadores, docentes, directores y familias se conectan en un solo lugar. "
    "Imagínate tomar asistencia georreferenciada en la cancha con un solo toque desde el celular, entregarle a cada alumno un carnet digital interactivo que lleva con orgullo en su móvil, y monitorear el rendimiento técnico y biométrico paso a paso. "
    "Ya sea que lideres una escuela de fútbol formativo, un club de patinaje, una academia de taekwondo, un conservatorio de música o una compañía de danza folclórica y urbana: "
    "SGA-CD pone la tecnología más avanzada a trabajar por tu talento. Con reportes claros, auditoría en tiempo real y la tranquilidad de tener la información segura en la nube. "
    "Lleva tu institución al nivel de prestigio y profesionalismo que se merece. Da el salto a la era digital con SGA-CD y siente el respaldo de una plataforma hecha a la medida de tu berraquera. Conócenos hoy mismo."
)

# 2. Guiones de los 3 Shorts (45s cada uno - Ritmo continuo sin pausas muertas)
GUION_SHORT_1 = (
    "¡Oiga, profe! En la cancha el talento sobra, pero el desorden con planillas de papel le resta nivel a su escuela de fútbol, patinaje o taekwondo. "
    "Con SGA-CD usted toma asistencia georreferenciada desde el celular, lleva el historial de rendimiento de sus atletas y le entrega a cada alumno su carnet digital. "
    "Menos papeleo y más campeones formados. Modernice su club hoy mismo con SGA-CD."
)

GUION_SHORT_2 = (
    "El arte y la cultura transforman a nuestra juventud, pero llevar una academia de danza o música con notas perdidas es un dolor de cabeza. "
    "Con SGA-CD organice sus talleres, audiciones, horarios de ensayo y eventos en una sola plataforma profesional. "
    "Sus artistas y familias conectados con la mejor tecnología. Pásese a SGA-CD."
)

GUION_SHORT_3 = (
    "¿Dirige una institución educativa, club o liga en Colombia? Es hora de dejar atrás los métodos del pasado. "
    "SGA-CD unifica el control de alumnos, docentes, escenarios y reportes en tiempo real desde la web y el móvil. "
    "La herramienta definitiva para directores que buscan la excelencia. Súmese a la revolución digital de SGA-CD."
)

async def generar_audios():
    print("-> Sintetizando audios neuronales colombianos con Edge-TTS (es-CO-GonzaloNeural)...")
    tareas = [
        ("edge-tts", "--voice", "es-CO-GonzaloNeural", "--rate=+5%", "--text", GUION_5_MINUTOS, "--write-media", "/app/output/audio_master_5min.mp3"),
        ("edge-tts", "--voice", "es-CO-GonzaloNeural", "--rate=+7%", "--text", GUION_SHORT_1, "--write-media", "/app/output/audio_short_1.mp3"),
        ("edge-tts", "--voice", "es-CO-GonzaloNeural", "--rate=+7%", "--text", GUION_SHORT_2, "--write-media", "/app/output/audio_short_2.mp3"),
        ("edge-tts", "--voice", "es-CO-GonzaloNeural", "--rate=+7%", "--text", GUION_SHORT_3, "--write-media", "/app/output/audio_short_3.mp3")
    ]
    for t in tareas:
        proc = await asyncio.create_subprocess_exec(*t)
        await proc.communicate()
    print("-> Todos los audios continuos generados exitosamente en /app/output/")

def renderizar_piezas():
    os.makedirs("/app/output", exist_ok=True)
    asyncio.run(generar_audios())

    # A. Video Master 5 Minutos (16:9 — 1920x1080)
    print("-> Renderizando Video Master de 5 Minutos (16:9)...")
    cmd_master = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=#070b14:s=1920x1080:d=120",
        "-i", "/app/output/audio_master_5min.mp3",
        "-filter_complex",
        "[0:v]drawtext=text='SGA-CD':fontcolor=#38bdf8:fontsize=76:x=(w-text_w)/2:y=(h-text_h)/2-120,"
        "drawtext=text='Plataforma Integral de Gestion Deportiva y Cultural':fontcolor=#f8fafc:fontsize=40:x=(w-text_w)/2:y=(h-text_h)/2-20,"
        "drawtext=text='Tecnologia de Vanguardia para Academias, Clubes y Colegios':fontcolor=#4ade80:fontsize=32:x=(w-text_w)/2:y=(h-text_h)/2+60[v]",
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p", "-shortest",
        "/app/output/sga_master_5min_youtube_16_9.mp4"
    ]
    subprocess.run(cmd_master, check=True)

    # B. Tres Videos Cortos (9:16 — 1080x1920 para Shorts / TikTok / Reels)
    shorts = [
        ("audio_short_1.mp3", "sga_short_1_deportes_9_16.mp4", "Formacion Deportiva"),
        ("audio_short_2.mp3", "sga_short_2_cultura_9_16.mp4", "Arte, Musica y Danza"),
        ("audio_short_3.mp3", "sga_short_3_institucional_9_16.mp4", "Gestion Institucional")
    ]
    for audio, output_name, title in shorts:
        print(f"-> Renderizando {output_name} (9:16)...")
        cmd_short = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "color=c=#0f172a:s=1080x1920:d=45",
            "-i", f"/app/output/{audio}",
            "-filter_complex",
            f"[0:v]drawtext=text='SGA-CD':fontcolor=#38bdf8:fontsize=84:x=(w-text_w)/2:y=(h-text_h)/2-180,"
            f"drawtext=text='{title}':fontcolor=#4ade80:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2-70,"
            "drawtext=text='Control Total en el Movil':fontcolor=#f8fafc:fontsize=36:x=(w-text_w)/2:y=(h-text_h)/2+40[v]",
            "-map", "[v]", "-map", "1:a",
            "-c:v", "libx264", "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p", "-shortest",
            f"/app/output/{output_name}"
        ]
        subprocess.run(cmd_short, check=True)

    print("-> ¡Suite Audiovisual completa generada en /app/output/!")

if __name__ == '__main__':
    renderizar_piezas()