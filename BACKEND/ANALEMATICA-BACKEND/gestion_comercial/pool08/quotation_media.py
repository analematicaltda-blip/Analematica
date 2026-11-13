"""Private, bounded marketing assets; no external URLs or arbitrary document rendering."""
import io,hashlib,tempfile,subprocess,json,math,os
from pathlib import Path
from .crm import CRMError
from .opportunities import uuid_ref
MAX_MEDIA=262144
class Media:
    def __init__(self,store,pricing):self.store,self.pricing=store,pricing
    def normalize(self,raw,mime):
        if not isinstance(raw,bytes) or not 0<len(raw)<=MAX_MEDIA:raise CRMError('QUOTE_MEDIA_LIMIT',413)
        if mime in ('image/png','image/jpeg','image/webp'):
            try:
                from PIL import Image
                with Image.open(io.BytesIO(raw)) as image:
                    if image.format not in ('PNG','JPEG','WEBP') or image.width*image.height>4000000 or getattr(image,'n_frames',1)!=1:raise ValueError()
                    image.load();clean=Image.new('RGB',image.size);clean.paste(image.convert('RGB'));out=io.BytesIO();clean.save(out,format='PNG');raw=out.getvalue();mime='image/png'
            except (ImportError,ModuleNotFoundError):raise CRMError('QUOTE_MEDIA_RUNTIME_REQUIRED',503) from None
            except Exception:raise CRMError('INVALID_QUOTE_IMAGE') from None
            if len(raw)>MAX_MEDIA:raise CRMError('QUOTE_MEDIA_LIMIT',413)
        elif mime in ('video/mp4','video/webm'):
            try:
                with tempfile.TemporaryDirectory(prefix='quote-media-') as directory:
                    source=Path(directory)/'source';source.write_bytes(raw);fmt='mov' if mime=='video/mp4' else 'matroska'
                    args=['ffprobe','-v','error','-protocol_whitelist','file,pipe','-f',fmt,'-i',str(source),'-show_streams','-show_format','-of','json']
                    result=subprocess.run(args,capture_output=True,timeout=8,check=True);meta=json.loads(result.stdout);videos=[s for s in meta.get('streams',[]) if s.get('codec_type')=='video'];duration=float(meta['format'].get('duration','nan'))
                    if len(videos)!=1 or not math.isfinite(duration) or not 0<duration<=120 or not 0<int(videos[0].get('width',0))*int(videos[0].get('height',0))<=2073600:raise ValueError()
                    target=Path(directory)/('clean.mp4' if mime=='video/mp4' else 'clean.webm')
                    subprocess.run(['ffmpeg','-v','error','-protocol_whitelist','file,pipe','-f',fmt,'-i',str(source),'-map','0:v:0','-map','0:a:0?','-map_metadata','-1','-c','copy','-y',str(target)],capture_output=True,timeout=8,check=True)
                    raw=target.read_bytes()
                    if len(raw)>MAX_MEDIA:raise ValueError()
            except FileNotFoundError:raise CRMError('QUOTE_MEDIA_RUNTIME_REQUIRED',503) from None
            except Exception:raise CRMError('INVALID_QUOTE_VIDEO') from None
        else:raise CRMError('QUOTE_MEDIA_TYPE_NOT_ALLOWED',415)
        return raw,mime
    def upload(self,ref,raw,mime):
        self.pricing.authority();uuid_ref(ref);original=hashlib.sha256(raw).hexdigest();data,mime=self.normalize(raw,mime);digest=hashlib.sha256(data).hexdigest()
        with self.store.transaction():
            self.pricing.authority();self.store.lock();prior=self.store.asset(ref)
            if prior:
                if prior['creator_ref']!=self.pricing.actor or prior['original_digest']!=original:raise CRMError('MEDIA_REQUEST_CONFLICT',409)
                return self.get(ref)|{'replayed':True}
            count,size=self.store.asset_usage()
            if count>=100 or size+len(data)>20*1024*1024:raise CRMError('QUOTE_MEDIA_QUOTA',413)
            self.store.save_asset(ref,self.pricing.actor,data,mime,digest,original)
        return self.get(ref)|{'replayed':False}
    def get(self,ref):
        self.pricing.authority();uuid_ref(ref);row=self.store.asset(ref)
        if row is None:raise CRMError('QUOTE_MEDIA_NOT_FOUND',404)
        if hashlib.sha256(row['data']).hexdigest()!=row['digest']:raise CRMError('QUOTE_MEDIA_INTEGRITY_REVIEW_REQUIRED',503)
        return {'id':ref,'mime':row['mime'],'sha256':row['digest'],'size':len(row['data'])}
    def bytes(self,ref):
        meta=self.get(ref);return self.store.asset(ref)['data'],meta['mime']
