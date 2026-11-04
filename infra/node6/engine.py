"""Bounded provider adapters and a real, local reel renderer."""
import base64
from dataclasses import dataclass, field
import io
import json
import os
from pathlib import Path
import re
import subprocess
import textwrap
import threading
import uuid

from PIL import Image, ImageDraw, ImageFont
import requests

class WorkerError(Exception):
    def __init__(self,message,status=503):super().__init__(message);self.status=status

@dataclass
class Config:
    token:str=field(default='',repr=False)
    api_key:str=field(default='',repr=False)
    text_model:str='gemini-2.5-flash'
    image_model:str='gemini-2.5-flash-image'
    colibri_url:str=''
    colibri_key:str=field(default='',repr=False)
    youtube_id:str=field(default='',repr=False)
    youtube_secret:str=field(default='',repr=False)
    youtube_refresh:str=field(default='',repr=False)
    output:Path=Path('/state/generated')
    @classmethod
    def environment(cls):
        return cls(youtube_id=os.getenv('YOUTUBE_CLIENT_ID',''),youtube_secret=os.getenv('YOUTUBE_CLIENT_SECRET',''),youtube_refresh=os.getenv('YOUTUBE_REFRESH_TOKEN',''),token=os.getenv('NODE6_TOKEN',''),api_key=os.getenv('GEMINI_API_KEY',''),text_model=os.getenv('GEMINI_TEXT_MODEL','gemini-2.5-flash'),image_model=os.getenv('GEMINI_IMAGE_MODEL','gemini-2.5-flash-image'),colibri_url=os.getenv('COLIBRI_BASE_URL',''),colibri_key=os.getenv('COLIBRI_API_KEY',''),output=Path(os.getenv('NODE6_OUTPUT','/state/generated')))

class Engine:
    def __init__(self,config):
        self.config=config;self.client=requests.Session();self.render_lock=threading.Lock();self.gemini_inference_verified=False
        config.output.mkdir(parents=True,exist_ok=True)
        settings=config.output/'.provider-settings.json'
        if settings.exists():
            saved=json.loads(settings.read_text())
            config.api_key=saved.get('api_key',config.api_key)
            config.text_model=saved.get('text_model',config.text_model)
            config.image_model=saved.get('image_model',config.image_model)
    def model(self,name):
        if not re.fullmatch(r'[A-Za-z0-9._-]{1,120}',name):raise WorkerError('Identificador de modelo no válido',400)
        return name
    def gemini(self,path,body=None):
        if not self.config.api_key:raise WorkerError('Configura una clave de Gemini API en el archivo privado.')
        url='https://generativelanguage.googleapis.com/v1beta/'+path
        try:
            response=self.client.request('POST' if body is not None else 'GET',url,headers={'x-goog-api-key':self.config.api_key},json=body,timeout=(10,90),allow_redirects=False)
        except requests.RequestException:raise WorkerError('No se pudo conectar con Gemini. Revisa conectividad y configuración.') from None
        if response.status_code!=200:
            # Never echo a provider response, request headers, prompt or credential.
            raise WorkerError('Gemini rechazó la solicitud (HTTP '+str(response.status_code)+'). Revisa clave, modelo, cuota y permisos.')
        if len(response.content)>20*1024*1024:raise WorkerError('Respuesta del proveedor demasiado grande',502)
        try:return response.json()
        except ValueError:raise WorkerError('Respuesta no válida del proveedor',502) from None
    def models(self):
        result=self.gemini('models?pageSize=100')
        return {'models':[{'name':item.get('name'),'methods':item.get('supportedGenerationMethods',[])} for item in result.get('models',[])]}
    def text(self,prompt,provider='gemini'):
        if provider=='colibri':
            if not self.config.colibri_url:raise WorkerError('Colibrí no está configurado. Gemini remoto no utiliza sus pesos locales.')
            headers={'Authorization':'Bearer '+self.config.colibri_key} if self.config.colibri_key else {}
            try:
                base=self.config.colibri_url.rstrip('/')
                if base.endswith('/v1'):base=base[:-3]
                catalog=self.client.get(base+'/v1/models',headers=headers,timeout=(5,10),allow_redirects=False)
                catalog.raise_for_status();model=catalog.json()['data'][0]['id']
                response=self.client.post(base+'/v1/chat/completions',headers=headers,json={'model':model,'messages':[{'role':'user','content':prompt}],'max_tokens':1024,'stream':False},timeout=(10,90),allow_redirects=False)
                response.raise_for_status();text=response.json()['choices'][0]['message']['content']
            except (requests.RequestException,KeyError,ValueError,IndexError):raise WorkerError('Colibrí no respondió correctamente') from None
            return {'provider':'colibri','text':text}
        body={'contents':[{'role':'user','parts':[{'text':prompt}]}],'generationConfig':{'maxOutputTokens':2048}}
        result=self.gemini('models/'+self.model(self.config.text_model)+':generateContent',body)
        parts=[part for candidate in result.get('candidates',[]) for part in candidate.get('content',{}).get('parts',[])]
        text='\n'.join(part['text'] for part in parts if isinstance(part.get('text'),str) and not part.get('thought'))
        if not text:raise WorkerError('El modelo no devolvió texto utilizable',502)
        self.gemini_inference_verified=True
        return {'provider':'gemini','model':self.config.text_model,'text':text}
    def image(self,prompt):
        result=self.gemini('models/'+self.model(self.config.image_model)+':generateContent',{'contents':[{'parts':[{'text':prompt}]}],'generationConfig':{'responseModalities':['IMAGE']}})
        for candidate in result.get('candidates',[]):
            for part in candidate.get('content',{}).get('parts',[]):
                data=part.get('inlineData',{})
                if data.get('mimeType') not in ['image/png','image/jpeg']:continue
                try:
                    payload=base64.b64decode(data['data'],validate=True)
                    if len(payload)>8*1024*1024:raise ValueError()
                    picture=Image.open(io.BytesIO(payload))
                    if picture.width*picture.height>16_777_216:raise ValueError()
                    picture.load()
                    name=uuid.uuid4().hex+'.png';picture.convert('RGB').save(self.config.output/name)
                except (ValueError,KeyError,OSError,Image.DecompressionBombError):raise WorkerError('Imagen no válida o demasiado grande',502) from None
                self.gemini_inference_verified=True
                return {'provider':'gemini','model':self.config.image_model,'filename':name,'artifact_url':'/artifacts/'+name}
        raise WorkerError('El modelo no devolvió una imagen; revisa su compatibilidad y permisos',502)
    def reel(self,title,caption,duration=4,image=None):
        if not self.render_lock.acquire(blocking=False):raise WorkerError('Hay otro render en curso; vuelve a intentarlo.',429)
        temp=None;output=None
        try:
            frame=Image.new('RGB',(1080,1920),'#070B14')
            if image:
                picture=self.artifact(image)
                if picture.suffix!='.png':raise WorkerError('El fondo debe ser una imagen PNG del nodo',400)
                from PIL import ImageOps
                frame=ImageOps.fit(Image.open(picture).convert('RGB'),(1080,1920))
                frame=Image.blend(frame,Image.new('RGB',frame.size,'#070B14'),.55)
            draw=ImageDraw.Draw(frame)
            font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
            heading=ImageFont.truetype(font,58);body=ImageFont.truetype(font,38)
            draw.rounded_rectangle((64,120,1016,1800),radius=48,outline='#38BDF8',width=3)
            draw.text((112,190),'SGA-CD',font=heading,fill='#38BDF8')
            draw.multiline_text((112,600),'\n'.join(textwrap.wrap(title,22)),font=heading,fill='#38BDF8',spacing=18)
            draw.multiline_text((112,1100),'\n'.join(textwrap.wrap(caption,34)),font=body,fill='#7DD3FC',spacing=14)
            draw.text((112,1640),'Deporte · Cultura · Formación',font=body,fill='#7DD3FC')
            stem=uuid.uuid4().hex;temp=self.config.output/(stem+'-frame.png');output=self.config.output/(stem+'.mp4');frame.save(temp)
            subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-y','-loop','1','-i',str(temp),'-t',str(duration),'-r','24','-c:v','libx264','-preset','ultrafast','-crf','28','-threads','2','-pix_fmt','yuv420p','-movflags','+faststart',str(output)],check=True,timeout=90,capture_output=True)
            return {'renderer':'ffmpeg','ai_video':False,'filename':output.name,'artifact_url':'/artifacts/'+output.name,'width':1080,'height':1920,'duration':duration}
        except (subprocess.SubprocessError,OSError):
            if output:output.unlink(missing_ok=True)
            raise WorkerError('No se pudo renderizar el reel',502) from None
        finally:
            if temp:temp.unlink(missing_ok=True)
            self.render_lock.release()
    def artifact(self,name):
        if not re.fullmatch(r'[a-f0-9]{32}\.(png|mp4|json)',name):raise WorkerError('Archivo no válido',404)
        path=self.config.output/name
        if not path.is_file() or not path.resolve().is_relative_to(self.config.output.resolve()):raise WorkerError('Archivo no encontrado',404)
        return path
    def draft(self,filename,title,description,platforms):
        artifact=self.artifact(filename)
        if artifact.suffix!='.mp4':raise WorkerError('Selecciona un reel del nodo',400)
        data={'status':'draft','published':False,'artifact':artifact.name,'title':title,'description':description,'platforms':platforms,'required':'Autorizar el canal de destino; el borrador por sí solo no publica contenido.'}
        name=uuid.uuid4().hex+'.json';(self.config.output/name).write_text(json.dumps(data,ensure_ascii=False,indent=2))
        return dict(data,filename=name,artifact_url='/artifacts/'+name)
