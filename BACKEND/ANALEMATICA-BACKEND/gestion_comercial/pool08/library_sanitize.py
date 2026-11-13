"""Bounded marketing-only decoders. Original bytes are never the publication bytes."""
import io,subprocess,tempfile,json,math
from pathlib import Path
from .crm import CRMError
MAX_UPLOAD=8*1024*1024
MAX_DELIVERY=16*1024*1024

def sanitize(raw,mime):
    if not isinstance(raw,bytes) or not 0<len(raw)<=MAX_UPLOAD:raise CRMError('LIBRARY_UPLOAD_LIMIT',413)
    if mime in ('image/png','image/jpeg','image/webp'):
        try:
            from PIL import Image,ImageOps
            with Image.open(io.BytesIO(raw)) as source:
                if source.format!={'image/png':'PNG','image/jpeg':'JPEG','image/webp':'WEBP'}[mime] or source.width*source.height>16000000 or getattr(source,'n_frames',1)!=1:raise ValueError()
                source.load();source=ImageOps.exif_transpose(source);source.thumbnail((2048,2048));mode='RGBA' if 'A' in source.getbands() or 'transparency' in source.info else 'RGB';clean=Image.new(mode,source.size);clean.paste(source.convert(mode));out=io.BytesIO();clean.save(out,format='PNG');data=out.getvalue();meta={'kind':'IMAGE','width':clean.width,'height':clean.height,'duration_seconds':None}
        except ImportError:raise CRMError('LIBRARY_DECODER_REQUIRED',503) from None
        except Exception:raise CRMError('INVALID_LIBRARY_IMAGE') from None
        target_mime='image/png'
    elif mime in ('video/mp4','video/webm'):
        try:
            with tempfile.TemporaryDirectory(prefix='owned-media-library-') as directory:
                source=Path(directory)/'input';source.write_bytes(raw);fmt='mov' if mime=='video/mp4' else 'matroska';options=['-enable_drefs','0','-use_absolute_path','0'] if fmt=='mov' else []
                probe=subprocess.run(['ffprobe','-v','error','-protocol_whitelist','file,pipe','-f',fmt,*options,'-i',str(source),'-show_streams','-show_format','-of','json'],capture_output=True,timeout=10,check=True);m=json.loads(probe.stdout);videos=[s for s in m.get('streams',[]) if s.get('codec_type')=='video'];duration=float(m['format'].get('duration','nan'))
                if len(videos)!=1 or not math.isfinite(duration) or not 0<duration<=120 or not 0<int(videos[0].get('width',0))*int(videos[0].get('height',0))<=2073600:raise ValueError()
                target=Path(directory)/('review.mp4' if mime=='video/mp4' else 'review.webm')
                codecs=['-c:v','libx264','-preset','veryfast','-crf','23','-pix_fmt','yuv420p','-c:a','aac','-movflags','+faststart'] if mime=='video/mp4' else ['-c:v','libvpx-vp9','-deadline','realtime','-cpu-used','6','-c:a','libopus']
                subprocess.run(['ffmpeg','-v','error','-nostdin','-protocol_whitelist','file,pipe','-f',fmt,*options,'-i',str(source),'-map','0:v:0','-map','0:a:0?','-map_metadata','-1','-map_metadata:s','-1','-map_chapters','-1','-sn','-dn','-vf','scale=trunc(iw/2)*2:trunc(ih/2)*2','-t','120',*codecs,'-threads','2','-fs',str(MAX_DELIVERY+1),'-y',str(target)],capture_output=True,timeout=45,check=True)
                with target.open('rb') as stream:data=stream.read(MAX_DELIVERY+1)
                if len(data)>MAX_DELIVERY:raise ValueError()
                probe=subprocess.run(['ffprobe','-v','error','-protocol_whitelist','file,pipe','-i',str(target),'-show_streams','-show_format','-of','json'],capture_output=True,timeout=10,check=True);out=json.loads(probe.stdout);video=next(s for s in out['streams'] if s.get('codec_type')=='video');actual=float(out['format']['duration'])
                if not math.isfinite(actual) or abs(actual-duration)>0.75:raise ValueError()
                meta={'kind':'VIDEO','width':int(video['width']),'height':int(video['height']),'duration_seconds':actual}
        except FileNotFoundError:raise CRMError('LIBRARY_DECODER_REQUIRED',503) from None
        except Exception:raise CRMError('INVALID_LIBRARY_VIDEO') from None
        target_mime=mime
    else:raise CRMError('LIBRARY_MARKETING_MEDIA_ONLY',415)
    if not 0<len(data)<=MAX_DELIVERY:raise CRMError('LIBRARY_DELIVERY_LIMIT',413)
    return data,target_mime,meta
