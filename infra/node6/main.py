import hmac
import json
import os
from dataclasses import replace
from pathlib import Path
from typing import Literal
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field, ValidationError, SecretStr
from fastapi.exceptions import RequestValidationError
from .engine import Config, Engine, WorkerError
from .youtube import YouTube

class Prompt(BaseModel):
    prompt:str=Field(min_length=1,max_length=6000)
    provider:Literal['gemini','colibri']='gemini'
class ImagePrompt(BaseModel):
    prompt:str=Field(min_length=1,max_length=6000)
    model_config={'extra':'forbid'}
class Reel(BaseModel):
    title:str=Field(min_length=1,max_length=90)
    caption:str=Field(default='',max_length=220)
    duration:int=Field(default=4,ge=1,le=15)
    image:str|None=None
class Draft(BaseModel):
    filename:str
    title:str=Field(min_length=1,max_length=100)
    description:str=Field(default='',max_length=2000)
    platforms:list[Literal['youtube','instagram','facebook','tiktok']]=Field(min_length=1,max_length=4)

class PrivateUpload(BaseModel):
    filename:str
    title:str=Field(min_length=1,max_length=100)
    description:str=Field(default='',max_length=5000)
    made_for_kids:bool
    confirm_private:Literal[True]
    model_config={'extra':'forbid'}

class ScopedUpload(PrivateUpload):
    workspace:str=Field(pattern=r'^(platform|tenant:[0-9]+)$')
    youtube_client_id:SecretStr
    youtube_client_secret:SecretStr
    youtube_refresh_token:SecretStr
class ProviderSettings(BaseModel):
    api_key:SecretStr
    text_model:str=Field(pattern=r'^[A-Za-z0-9._-]{1,120}$')
    image_model:str=Field(pattern=r'^[A-Za-z0-9._-]{1,120}$')
    model_config={'extra':'forbid'}

TOOLS=[
 {'name':'node6_status','description':'Estado del nodo; no hace llamadas de IA.','inputSchema':{'type':'object','properties':{}}},
 {'name':'generate_script','description':'Genera texto o guion con Gemini o Colibrí configurado.','inputSchema':Prompt.model_json_schema()},
 {'name':'generate_image','description':'Genera una imagen mediante la API de Gemini configurada. Puede consumir cuota.','inputSchema':ImagePrompt.model_json_schema()},
 {'name':'render_reel','description':'Crea un MP4 vertical real con FFmpeg. No es video generado por Veo.','inputSchema':Reel.model_json_schema()},
 {'name':'prepare_social_draft','description':'Prepara un borrador de publicación. Nunca envía contenido a una red social.','inputSchema':Draft.model_json_schema()}
]

def create_app(config=None):
    config=config or Config.environment();engine=Engine(config)
    app=FastAPI(title='SGA-CD · Nodo 6 · Estudio de pruebas',version='0.1.0')
    bearer=HTTPBearer(auto_error=False)
    def auth(credentials:HTTPAuthorizationCredentials|None=Depends(bearer)):
        if not config.token:raise HTTPException(503,'Configura NODE6_TOKEN')
        if credentials is None or not hmac.compare_digest(credentials.credentials,config.token):raise HTTPException(401,'Acceso no autorizado')
    @app.exception_handler(WorkerError)
    async def failure(request,error):return JSONResponse(status_code=error.status,content={'detail':str(error)})
    @app.exception_handler(RequestValidationError)
    async def invalid(request,error):return JSONResponse(status_code=422,content={'detail':'Datos no válidos; no se devolvieron valores de la solicitud.'})
    @app.middleware('http')
    async def headers(request:Request,call_next):
        response=await call_next(request);response.headers['Cache-Control']='no-store';response.headers['X-Content-Type-Options']='nosniff';response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' blob:; media-src 'self' blob:; frame-ancestors 'none'; base-uri 'none'";return response
    @app.get('/')
    def studio():return FileResponse(Path(__file__).with_name('studio.html'))
    @app.get('/studio.js')
    def studio_js():return FileResponse(Path(__file__).with_name('studio.js'),media_type='text/javascript')
    @app.get('/studio.css')
    def studio_css():return FileResponse(Path(__file__).with_name('studio.css'),media_type='text/css')
    @app.get('/health')
    def health():return {'status':'online','node':6}
    def status():return {'node':6,'gemini_key_configured':bool(config.api_key),'text_model':config.text_model,'image_model':config.image_model,'remote_inference_verified':engine.gemini_inference_verified,'colibri_configured':bool(config.colibri_url),'local_weights_required_for_gemini':False,'reel_renderer':'ffmpeg','social_publishing':'YouTube private only, requires channel OAuth; other networks draft only','matrix_integration':'MCP adapter; registration and kernel credentials required','ai_video':'Not configured; Gemini text access does not imply Veo access'}
    @app.get('/status',dependencies=[Depends(auth)])
    def get_status():return status()
    @app.get('/providers/gemini/models',dependencies=[Depends(auth)])
    def models():return engine.models()
    @app.post('/studio/script',dependencies=[Depends(auth)])
    def script(body:Prompt):return engine.text(body.prompt,body.provider)
    @app.post('/studio/image',dependencies=[Depends(auth)])
    def image(body:ImagePrompt):return engine.image(body.prompt)
    @app.post('/studio/reel',dependencies=[Depends(auth)])
    def reel(body:Reel):return engine.reel(body.title,body.caption,body.duration,body.image)
    @app.post('/social/draft',dependencies=[Depends(auth)])
    def draft(body:Draft):return engine.draft(body.filename,body.title,body.description,body.platforms)
    @app.post('/youtube/upload-private',dependencies=[Depends(auth)])
    def youtube(body:PrivateUpload):return YouTube(engine).upload(body.filename,body.title,body.description,body.made_for_kids)
    @app.post('/internal/youtube/upload-private',dependencies=[Depends(auth)])
    def scoped_youtube(body:ScopedUpload):
        scoped=Engine(replace(config,youtube_id=body.youtube_client_id.get_secret_value(),youtube_secret=body.youtube_client_secret.get_secret_value(),youtube_refresh=body.youtube_refresh_token.get_secret_value()))
        scoped.client=engine.client
        return YouTube(scoped,scope=body.workspace).upload(body.filename,body.title,body.description,body.made_for_kids)
    @app.put('/internal/providers/gemini',dependencies=[Depends(auth)])
    def provider(body:ProviderSettings):
        values={'api_key':body.api_key.get_secret_value().strip(),'text_model':body.text_model,'image_model':body.image_model}
        if not values['api_key']:raise HTTPException(422,'Completa la clave del proveedor.')
        path=config.output/'.provider-settings.json';temp=path.with_suffix('.tmp')
        with open(temp,'w',opener=lambda name,flags:os.open(name,flags,0o600)) as stream:json.dump(values,stream)
        os.replace(temp,path);config.api_key=values['api_key'];config.text_model=values['text_model'];config.image_model=values['image_model'];engine.gemini_inference_verified=False
        return {'configured':True,'verified':False}
    @app.get('/artifacts/{filename}',dependencies=[Depends(auth)])
    def artifact(filename:str):return FileResponse(engine.artifact(filename),filename=filename)
    @app.post('/mcp',dependencies=[Depends(auth)])
    def mcp(body:dict):
        ident=body.get('id');method=body.get('method');params=body.get('params',{})
        if not isinstance(params,dict):return {'jsonrpc':'2.0','id':ident,'error':{'code':-32602,'message':'Parámetros no válidos'}}
        if method=='notifications/initialized':return Response(status_code=202)
        if method=='initialize':result={'protocolVersion':'2025-03-26','capabilities':{'tools':{}},'serverInfo':{'name':'sgacd-node6','version':'0.1.0'}}
        elif method=='tools/list':result={'tools':TOOLS}
        elif method=='ping':result={}
        elif method=='tools/call':
            name=params.get('name');arguments=params.get('arguments',{})
            try:
                if name=='node6_status':value=status()
                elif name=='generate_script':value=script(Prompt.model_validate(arguments))
                elif name=='generate_image':value=image(ImagePrompt.model_validate(arguments))
                elif name=='render_reel':value=reel(Reel.model_validate(arguments))
                elif name=='prepare_social_draft':value=draft(Draft.model_validate(arguments))
                else:return {'jsonrpc':'2.0','id':ident,'error':{'code':-32601,'message':'Herramienta no disponible'}}
                import json
                result={'content':[{'type':'text','text':json.dumps(value,ensure_ascii=False)}]}
            except (ValidationError,WorkerError) as error:
                result={'isError':True,'content':[{'type':'text','text':str(error) if isinstance(error,WorkerError) else 'Parámetros no válidos'}]}
        else:return {'jsonrpc':'2.0','id':ident,'error':{'code':-32601,'message':'Método no disponible'}}
        return {'jsonrpc':'2.0','id':ident,'result':result}
    app.state.engine=engine
    return app

app=create_app()
