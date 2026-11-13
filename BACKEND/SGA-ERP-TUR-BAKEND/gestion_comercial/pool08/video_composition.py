"""Bounded local branded composition, never a generative-video or voice-cloning claim."""
import hashlib,io,json,math,re,subprocess,tempfile,textwrap
from pathlib import Path
from .crm import CRMError,digest,text
SIZES={'REEL':(360,640),'SQUARE':(480,480),'LANDSCAPE':(640,360)}
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def spec(value):
    if not isinstance(value,dict) or set(value)!={'format','brand','scenes','voice','music'} or not isinstance(value['format'],str) or value['format'] not in SIZES:raise CRMError('VIDEO_INVALID_COMPOSITION')
    if not isinstance(value['scenes'],list) or not 1<=len(value['scenes'])<=6:raise CRMError('VIDEO_INVALID_SCENES')
    scenes=[]
    for row in value['scenes']:
        if not isinstance(row,dict) or set(row)!={'text','seconds'} or type(row['seconds'])!=int or not 1<=row['seconds']<=10:raise CRMError('VIDEO_INVALID_SCENES')
        scenes.append({'text':text(row['text'],180),'seconds':row['seconds']})
    if sum(x['seconds'] for x in scenes)>30:raise CRMError('VIDEO_DURATION_LIMIT')
    result={'format':value['format'],'brand':text(value['brand'],80),'scenes':scenes}
    for role in ['voice','music']:
        ref=value[role]
        if ref is not None:
            if not isinstance(ref,dict) or set(ref)!={'item_id','version','sha256','rights_confirmed'} or type(ref['version'])!=int or not 1<=ref['version']<=20 or ref['rights_confirmed'] is not True or not isinstance(ref['sha256'],str) or not re.fullmatch('[a-f0-9]{64}',ref['sha256']):raise CRMError('VIDEO_AUDIO_AUTHORIZATION_REQUIRED')
            from .opportunities import uuid_ref
            uuid_ref(ref['item_id'])
        result[role]=ref
    return result

def fingerprint():
    try:
        result=subprocess.run(['ffmpeg','-version'],capture_output=True,timeout=5,check=True)
        from PIL import __version__
        return hashlib.sha256(Path(__file__).read_bytes()+result.stdout+Path(FONT).read_bytes()+__version__.encode()).hexdigest()
    except (OSError,subprocess.SubprocessError):raise CRMError('VIDEO_RENDERER_REQUIRED',503) from None

def sources(crm,plan):
    from .library_api import service
    from .media_library import usable
    library=service(crm);out={}
    for role in ['voice','music']:
        ref=plan[role]
        if ref is None:continue
        item=library.get(ref['item_id'])
        if len(item['versions'])!=ref['version']:raise CRMError('VIDEO_AUDIO_REVIEW_STALE',409)
        v=item['versions'][-1]
        if item['approved_digest']!=digest(v) or not usable(v):raise CRMError('VIDEO_AUDIO_AUTHORIZATION_REQUIRED',409)
        raw,mime=library.bytes(ref['item_id'],ref['version'],'delivery')
        if mime!='video/mp4' or hashlib.sha256(raw).hexdigest()!=ref['sha256']:raise CRMError('VIDEO_AUDIO_REVIEW_STALE',409)
        out[role]=raw
    return out

def render(plan,expected_digest,audio=None):
    plan=spec(plan);audio=audio or {}
    if fingerprint()!=expected_digest:raise CRMError('VIDEO_RENDERER_CHANGED',503)
    if set(audio)!={r for r in ['voice','music'] if plan[r] is not None}:raise CRMError('VIDEO_AUDIO_AUTHORIZATION_REQUIRED',409)
    from PIL import Image,ImageDraw,ImageFont
    duration=sum(x['seconds'] for x in plan['scenes']);width,height=SIZES[plan['format']]
    try:
        with tempfile.TemporaryDirectory(prefix='owned-video-composition-') as directory:
            folder=Path(directory);lines=[];subtitles=[];elapsed=0
            for i,scene in enumerate(plan['scenes']):
                image=Image.new('RGB',(width,height),(17,48,75));draw=ImageDraw.Draw(image);font=ImageFont.truetype(FONT,22);small=ImageFont.truetype(FONT,17)
                draw.rectangle((0,0,width,8),fill=(96,190,240));draw.multiline_text((22,30),'\n'.join(textwrap.wrap(plan['brand'],max(12,(width-44)//13))),font=small,fill='white',spacing=6)
                caption='\n'.join(textwrap.wrap(scene['text'],max(12,(width-44)//13)))
                draw.multiline_text((22,max(130,height//3)),caption,font=font,fill='white',spacing=10)
                draw.text((22,height-36),'Composición · borrador',font=small,fill=(150,215,255))
                name='scene'+str(i)+'.png';image.save(folder/name);lines.extend(["file '"+name+"'",'duration '+str(scene['seconds'])]);subtitles.append({'start_seconds':elapsed,'end_seconds':elapsed+scene['seconds'],'text':scene['text']});elapsed+=scene['seconds']
            lines.append("file '"+name+"'");(folder/'scenes.txt').write_text('\n'.join(lines)+'\n')
            command=['ffmpeg','-v','error','-nostdin','-protocol_whitelist','file,pipe','-f','concat','-safe','1','-i','scenes.txt']
            for role in ['voice','music']:
                if role not in audio:continue
                raw=audio[role]
                if not isinstance(raw,bytes) or not 0<len(raw)<=16*1024*1024 or hashlib.sha256(raw).hexdigest()!=plan[role]['sha256']:raise CRMError('VIDEO_AUDIO_REVIEW_STALE',409)
                path=folder/(role+'.mp4');path.write_bytes(raw)
                probe=subprocess.run(['ffprobe','-v','error','-protocol_whitelist','file,pipe','-f','mov','-enable_drefs','0','-use_absolute_path','0','-i',str(path),'-show_streams','-show_format','-of','json'],capture_output=True,check=True,timeout=10)
                info=json.loads(probe.stdout);streams=[s for s in info['streams'] if s['codec_type']=='audio'];length=float(info['format']['duration'])
                if len(streams)!=1 or not math.isfinite(length) or length<duration or length>120:raise CRMError('VIDEO_AUDIO_DURATION_OR_STREAM_INVALID',409)
                command+=['-protocol_whitelist','file,pipe','-f','mov','-enable_drefs','0','-use_absolute_path','0','-i',str(path)]
            command+=['-map','0:v:0']
            if len(audio)==2:command+=['-filter_complex','[1:a]volume=1[v];[2:a]volume=0.2[m];[v][m]amix=inputs=2:normalize=0[a]','-map','[a]']
            elif audio:command+=['-map','1:a:0']
            command+=['-t',str(duration),'-vf','fps=24,tpad=stop_mode=clone:stop_duration=1','-r','24','-c:v','libx264','-preset','veryfast','-crf','25','-pix_fmt','yuv420p','-c:a','aac','-ac','2','-ar','48000','-map_metadata','-1','-map_chapters','-1','-sn','-dn','-threads','2','-movflags','+faststart','-fs',str(8*1024*1024+1),'-y','result.mp4']
            subprocess.run(command,cwd=folder,capture_output=True,timeout=90,check=True)
            data=(folder/'result.mp4').read_bytes()
            if not 0<len(data)<=8*1024*1024:raise ValueError()
            probe=subprocess.run(['ffprobe','-v','error','-protocol_whitelist','file,pipe','-i',str(folder/'result.mp4'),'-show_streams','-show_format','-of','json'],capture_output=True,timeout=10,check=True);info=json.loads(probe.stdout);video=[s for s in info['streams'] if s['codec_type']=='video'];has_audio=any(s['codec_type']=='audio' for s in info['streams'])
            if len(video)!=1 or video[0]['codec_name']!='h264' or (video[0]['width'],video[0]['height'])!=(width,height) or abs(float(info['format']['duration'])-duration)>0.15 or has_audio!=bool(audio):raise ValueError()
            if fingerprint()!=expected_digest:raise CRMError('VIDEO_RENDERER_CHANGED',503)
            trace={'provider':'ffmpeg-local-composition','model_digest':expected_digest,'model_digest_verification':'RENDERER_SOURCE_AND_VERSION','composition':True,'generative_video':False,'voice_cloned':False,'voice_authorized_declaration':plan['voice'] is not None,'music_authorized_declaration':plan['music'] is not None,'rights_authenticity_verified':False,'duration_seconds':duration,'width':width,'height':height,'subtitles':subtitles,'audio_source_hashes':{k:hashlib.sha256(v).hexdigest() for k,v in audio.items()},'review_required':True,'published':False}
            return data,'video/mp4',trace
    except CRMError:raise
    except FileNotFoundError:raise CRMError('VIDEO_RENDERER_REQUIRED',503) from None
    except (OSError,ValueError,KeyError,subprocess.SubprocessError):raise CRMError('VIDEO_COMPOSITION_FAILED',503) from None

if __name__=="__main__":
    print(json.dumps({"adapter":"ffmpeg-composition","model":"ffmpeg-composition-v1","model_digest":fingerprint(),"composition":True,"generative_video":False,"worker_enabled_by_this_command":False}))
