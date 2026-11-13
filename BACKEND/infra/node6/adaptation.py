"""Bounded MP4 adaptations: preserve the source, fit/pad the frame, never silently trim."""
import json
import subprocess
import uuid
from .engine import WorkerError

PROFILES={
 'instagram':dict(width=1080,height=1920,max_seconds=90,max_mb=40),
 'tiktok':dict(width=1080,height=1920,max_seconds=60,max_mb=40),
 'facebook':dict(width=1080,height=1080,max_seconds=90,max_mb=40),
 'x':dict(width=1280,height=720,max_seconds=140,max_mb=40),
 'whatsapp':dict(width=480,height=854,max_seconds=60,max_mb=15),
 'gmail':dict(width=1280,height=720,max_seconds=140,max_mb=15),
 'youtube':dict(width=1080,height=1920,max_seconds=180,max_mb=40),
}

def adapt(engine,filename,profile):
    if profile not in PROFILES:raise WorkerError('Plataforma de adaptación no disponible.',400)
    source=engine.artifact(filename)
    if source.suffix!='.mp4':raise WorkerError('Selecciona un video MP4.',400)
    if source.stat().st_size>40*1024*1024:raise WorkerError('El video supera el límite de esta demo (40 MB).',422)
    if not engine.render_lock.acquire(blocking=False):raise WorkerError('Hay otro render en curso.',429)
    output=None
    try:
        result=subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(source)],capture_output=True,check=True,timeout=15)
        metadata=json.loads(result.stdout);spec=PROFILES[profile];duration=float(metadata['format']['duration'])
        videos=[s for s in metadata['streams'] if s.get('codec_type')=='video']
        if not videos or not 0<duration<=spec['max_seconds']:raise WorkerError('La duración no es compatible. Crea un clip más corto; el original se conserva.',422)
        if videos[0]['width']*videos[0]['height']>3840*2160:raise WorkerError('La resolución de entrada supera el límite de esta demo.',422)
        width,height=spec['width'],spec['height'];output=engine.config.output/(uuid.uuid4().hex+'.mp4')
        filters=f'scale={width}:{height}:force_original_aspect_ratio=decrease:force_divisible_by=2,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=0x070B14,setsar=1'
        command=['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-y','-i',str(source),'-map','0:v:0','-map','0:a:0?','-vf',filters,'-r','24','-c:v','libx264','-profile:v','main','-preset','veryfast','-crf','26','-maxrate','1200k' if profile=='whatsapp' else '3500k','-bufsize','2400k' if profile=='whatsapp' else '7000k','-threads','2','-pix_fmt','yuv420p','-c:a','aac','-b:a','96k','-ar','44100','-movflags','+faststart',str(output)]
        subprocess.run(command,capture_output=True,check=True,timeout=150)
        if output.stat().st_size>spec['max_mb']*1024*1024:raise WorkerError('La adaptación supera el tamaño permitido; prepara un clip más corto.',422)
        return {'filename':output.name,'profile':profile,'width':width,'height':height,'duration':duration,'bytes':output.stat().st_size,'source_preserved':True}
    except (subprocess.SubprocessError,OSError,ValueError,KeyError):
        if output:output.unlink(missing_ok=True)
        raise WorkerError('No se pudo adaptar el video.',502) from None
    except WorkerError:
        if output:output.unlink(missing_ok=True)
        raise
    finally:engine.render_lock.release()
