"""Versioned local delivery profiles. No network upload, inferred framing or quality invention."""
import io,json,hashlib,math,subprocess,tempfile,copy
from pathlib import Path
from .crm import CRMError
from .library_sanitize import sanitize,MAX_DELIVERY
VERSION='1.0'
PROFILES={
 'image-vertical-v1':{'kind':'IMAGE','width':1080,'height':1920,'mime':'image/png'},
 'image-square-v1':{'kind':'IMAGE','width':1080,'height':1080,'mime':'image/png'},
 'image-landscape-v1':{'kind':'IMAGE','width':1920,'height':1080,'mime':'image/png'},
 'video-vertical-v1':{'kind':'VIDEO','width':720,'height':1280,'mime':'video/mp4'},
 'video-square-v1':{'kind':'VIDEO','width':720,'height':720,'mime':'video/mp4'},
 'video-landscape-v1':{'kind':'VIDEO','width':1280,'height':720,'mime':'video/mp4'}}
def catalog():return {'version':VERSION,'profiles':copy.deepcopy(PROFILES),'max_output_bytes':MAX_DELIVERY,'max_duration_seconds':120,'network_profiles_certified':False,'neural_reframing':False,'quality_gain_claimed':False,'subtitle_policy':'BURNED_ONLY_NO_TEXT_TRACKS'}
def options(data):
 if not isinstance(data,dict) or set(data)!={'source_version','source_sha256','profile','profile_version','mode','allow_upscale','confirmed_crop','audio','subtitles'}:raise CRMError('INVALID_ADAPTATION_OPTIONS')
 if type(data['source_version'])!=int or not 1<=data['source_version']<=20 or not isinstance(data['source_sha256'],str) or len(data['source_sha256'])!=64 or any(c not in '0123456789abcdef' for c in data['source_sha256']):raise CRMError('INVALID_ADAPTATION_SOURCE')
 if data['profile_version']!=VERSION or not isinstance(data['profile'],str) or data['profile'] not in PROFILES:raise CRMError('ADAPTATION_PROFILE_REQUIRED')
 if data['mode'] not in ('PAD','CROP') or type(data['allow_upscale'])!=bool or type(data['confirmed_crop'])!=bool or data['mode']=='CROP' and not data['confirmed_crop']:raise CRMError('ADAPTATION_CROP_REVIEW_REQUIRED')
 profile=PROFILES[data['profile']]
 if data['subtitles']!='BURNED_ONLY_NO_TEXT_TRACKS' or data['audio'] not in (('NONE',) if profile['kind']=='IMAGE' else ('KEEP','MUTE')):raise CRMError('ADAPTATION_AUDIO_OR_SUBTITLES_POLICY_REQUIRED')
 return dict(profile)
def _probe(path,fmt='mov'):
 extra=['-enable_drefs','0','-use_absolute_path','0'] if fmt=='mov' else []
 result=subprocess.run(['ffprobe','-v','error','-protocol_whitelist','file,pipe','-f',fmt,*extra,'-i',str(path),'-show_streams','-show_format','-of','json'],capture_output=True,timeout=10,check=True)
 return json.loads(result.stdout)
def adapt(raw,mime,data):
 target=options(data);source,normalized,info=sanitize(raw,mime)
 if info['kind']!=target['kind']:raise CRMError('ADAPTATION_MEDIA_TYPE_MISMATCH')
 w,h=target['width'],target['height'];sw,sh=info['width'],info['height'];display_width=sw;sample_aspect='1:1'
 if info['kind']=='VIDEO':
  try:
   with tempfile.TemporaryDirectory(prefix='owned-adaptation-probe-') as d:
    file=Path(d)/'source';file.write_bytes(source);source_probe=_probe(file,'mov' if normalized=='video/mp4' else 'matroska')
   video=next(v for v in source_probe['streams'] if v.get('codec_type')=='video');sample_aspect=video.get('sample_aspect_ratio','1:1');num,den=map(int,sample_aspect.split(':'))
   if num<=0 or den<=0 or not .1<=num/den<=10:raise ValueError()
   display_width=sw*num/den
  except FileNotFoundError:raise CRMError('ADAPTATION_DECODER_REQUIRED',503) from None
  except (ValueError,KeyError,StopIteration,OSError,subprocess.SubprocessError):raise CRMError('ADAPTATION_INVALID_SAMPLE_ASPECT',422) from None
 ratio=max(w/display_width,h/sh) if data['mode']=='CROP' else min(w/display_width,h/sh)
 if ratio>1 and not data['allow_upscale'] and data['mode']=='CROP':raise CRMError('ADAPTATION_UPSCALE_REQUIRES_CONSENT',409)
 factor=ratio if data['allow_upscale'] else min(1,ratio)
 trace={'kind':target['kind'],'width':w,'height':h,'duration_seconds':None,'adaptation':{'profile':data['profile'],'profile_version':VERSION,'mode':data['mode'],'allow_upscale':data['allow_upscale'],'source_width':sw,'source_height':sh,'source_sample_aspect_ratio':sample_aspect,'source_original_sha256':hashlib.sha256(raw).hexdigest(),'normalized_sha256':hashlib.sha256(source).hexdigest(),'source_version':data['source_version'],'source_delivery_sha256':data['source_sha256'],'scaled_up':factor>1,'neural_reframing':False,'quality_gain_claimed':False,'audio_policy':data['audio'],'subtitle_policy':data['subtitles'],'burned_text_may_be_cropped':data['mode']=='CROP','network_profiles_certified':False}}
 try:
  if info['kind']=='IMAGE':
   from PIL import Image
   with Image.open(io.BytesIO(source)) as image:
    image.load();rw,rh=max(1,round(sw*factor)),max(1,round(sh*factor));image=image.convert('RGBA').resize((rw,rh),Image.Resampling.LANCZOS)
    if data['mode']=='CROP':image=image.crop(((rw-w)//2,(rh-h)//2,(rw+w)//2,(rh+h)//2))
    else:
     canvas=Image.new('RGBA',(w,h),(17,48,75,255));canvas.alpha_composite(image,((w-rw)//2,(h-rh)//2));image=canvas
    result=io.BytesIO();image.save(result,format='PNG');output=result.getvalue()
   with Image.open(io.BytesIO(output)) as check:
    check.load()
    if check.size!=(w,h):raise ValueError()
  else:
   with tempfile.TemporaryDirectory(prefix='owned-media-adaptation-') as directory:
    folder=Path(directory);inp=folder/'source';inp.write_bytes(source);dest=folder/'delivery.mp4';fmt='mov' if normalized=='video/mp4' else 'matroska';input_opts=['-enable_drefs','0','-use_absolute_path','0'] if fmt=='mov' else []
    input_audio=any(s.get('codec_type')=='audio' for s in _probe(inp,fmt)['streams'])
    rw,rh=max(2,round(display_width*factor/2)*2),max(2,round(sh*factor/2)*2)
    if data['mode']=='CROP':rw,rh=max(w,rw),max(h,rh)
    else:rw,rh=min(w,rw),min(h,rh)
    transform=f'scale={rw}:{rh}:flags=lanczos,'+(f'crop={w}:{h}' if data['mode']=='CROP' else f'pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=0x11304b')+',setsar=1'
    command=['ffmpeg','-v','error','-nostdin','-protocol_whitelist','file,pipe','-f',fmt,*input_opts,'-i',str(inp),'-map','0:v:0']
    command+=['-map','0:a:0?','-c:a','aac','-b:a','128k','-ac','2','-ar','48000'] if data['audio']=='KEEP' else ['-an']
    command+=['-vf',transform,'-c:v','libx264','-preset','veryfast','-crf','23','-maxrate','4M','-bufsize','8M','-pix_fmt','yuv420p','-threads','2','-t','120','-map_metadata','-1','-map_metadata:s','-1','-map_chapters','-1','-sn','-dn','-movflags','+faststart','-fs',str(MAX_DELIVERY+1),'-y',str(dest)]
    subprocess.run(command,capture_output=True,timeout=90,check=True);output=dest.read_bytes();actual=_probe(dest);videos=[s for s in actual['streams'] if s.get('codec_type')=='video'];audios=[s for s in actual['streams'] if s.get('codec_type')=='audio'];duration=float(actual['format']['duration'])
    if len(videos)!=1 or (videos[0]['width'],videos[0]['height'])!=(w,h) or videos[0]['codec_name']!='h264' or not math.isfinite(duration) or abs(duration-info['duration_seconds'])>.75 or bool(audios)!=(input_audio and data['audio']=='KEEP') or any(s.get('codec_type')=='subtitle' for s in actual['streams']):raise ValueError()
    trace['duration_seconds']=duration;trace['adaptation']['content_width']=rw;trace['adaptation']['content_height']=rh;trace['adaptation']['lossy_video_transcoding']=True;trace['adaptation']['source_audio_present']=input_audio;trace['adaptation']['output_audio_present']=bool(audios);trace['adaptation']['video_codec']='h264';trace['adaptation']['crf']=23
  if not 0<len(output)<=MAX_DELIVERY:raise CRMError('ADAPTATION_OUTPUT_LIMIT',413)
  trace['adaptation']['output_bytes']=len(output)
  return output,target['mime'],trace
 except CRMError:raise
 except FileNotFoundError:raise CRMError('ADAPTATION_DECODER_REQUIRED',503) from None
 except (OSError,ValueError,KeyError,subprocess.SubprocessError):raise CRMError('ADAPTATION_FAILED',503) from None
