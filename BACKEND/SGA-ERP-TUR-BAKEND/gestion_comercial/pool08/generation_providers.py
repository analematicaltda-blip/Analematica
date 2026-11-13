"""Strict local model adapters. No external URLs, proxy inheritance or fabricated fallback."""
import base64,hashlib,json,os,re
from urllib.parse import urlsplit
import httpx
from .crm import CRMError,digest
from .contract import SYSTEM
from .library_sanitize import sanitize
MAX_RESPONSE=12*1024*1024
PROMPT_PREFIX='Produce el contenido comercial solicitado en español. No inventes hechos, precios, testimonios ni autorizaciones. Entrega un borrador para revisión humana.\n'

def endpoint(adapter):
    defaults={'ollama':'http://127.0.0.1:11434','colibri':'http://127.0.0.1:8080','sd-webui':'http://127.0.0.1:7860','node6-text':'http://127.0.0.1:8606','node6-image':'http://127.0.0.1:8606','open-gen-ai':'http://127.0.0.1:3000'}
    try:
        registry=json.loads(os.environ.get('COMMERCIAL_GENERATION_ENDPOINTS','{}'));value=registry.get(SYSTEM,{}).get(adapter,defaults[adapter]);u=urlsplit(value)
        if u.scheme not in ('http','https') or u.hostname not in ('127.0.0.1','localhost','ollama','colibri','node6','open-gen-ai','stable-diffusion') or u.port not in (11434,8080,8606,3000,7860) or u.username or u.password or u.query or u.fragment or u.path not in ('','/'):raise ValueError()
        return value.rstrip('/')
    except (ValueError,KeyError,TypeError,AttributeError):raise CRMError('GENERATION_ENDPOINT_CONFIGURATION_REQUIRED',503) from None

def remote_approved(scope,provider,profile_id,configuration_digest):
    try:
        values=json.loads(os.environ.get('COMMERCIAL_GENERATION_REMOTE_APPROVALS','{}'))
        return isinstance(values,dict) and values.get(SYSTEM+':'+scope+':'+(provider or '-')+':'+profile_id)==configuration_digest
    except (ValueError,TypeError):return False

def credentials(job):
    try:
        values=json.loads(os.environ.get('COMMERCIAL_GENERATION_SECRET_BINDINGS','{}'))
        name=values.get(SYSTEM+':'+job['scope']+':'+(job.get('provider_ref') or '-')+':'+job['profile']['id'])
        if name is None:return {}
        if not isinstance(name,str) or not (re.fullmatch('COMMERCIAL_GENERATION_SECRET_[A-Z0-9_]{1,80}',name) or name in ('NODE6_TOKEN','COLIBRI_API_KEY')):raise ValueError()
        value=os.environ.get(name,'')
        if not value or len(value)>4096 or any(ord(c)<32 for c in value):raise ValueError()
        return {'Authorization':'Bearer '+value}
    except (ValueError,TypeError,AttributeError):raise CRMError('GENERATION_SECRET_BINDING_REQUIRED',503) from None

def _image_artifact(client,base,reference,headers):
    try:
        u=urlsplit(reference)
        expected=urlsplit(base)
        if u.scheme and u.scheme!='http' or u.hostname and u.hostname not in ({'localhost','127.0.0.1'} if expected.hostname in ('localhost','127.0.0.1') else {expected.hostname}) or u.port and u.port!=expected.port or u.username or u.password or u.query or u.fragment:raise ValueError()
        if not re.fullmatch(r'/(artifacts|assets/generated)/[A-Za-z0-9_-]{1,100}\.(png|jpg|jpeg|webp)',u.path):raise ValueError()
        with client.stream('GET',base+u.path,headers=headers) as response:
            if response.status_code!=200:raise ValueError()
            raw=bytearray()
            for chunk in response.iter_bytes():
                raw.extend(chunk)
                if len(raw)>8*1024*1024:raise ValueError()
            mime=response.headers.get('content-type','').split(';')[0]
        data,mime,media=sanitize(bytes(raw),mime)
        if media['kind']!='IMAGE':raise ValueError()
        return data,mime,{'source_sha256':hashlib.sha256(raw).hexdigest(),'media':media}
    except (ValueError,TypeError,httpx.HTTPError,CRMError):raise CRMError('GENERATION_INVALID_IMAGE_RESULT',503) from None

def profiles(scope,provider):
    try:
        raw=json.loads(os.environ.get('COMMERCIAL_GENERATION_PROFILES','{}'))
        group=raw.get(SYSTEM+':'+scope+':'+(provider or '-'),{})
        if not isinstance(group,dict) or len(group)>10:raise ValueError()
        result={}
        for key,p in group.items():
            if not isinstance(key,str) or not re.fullmatch('[a-z0-9-]{1,40}',key) or not isinstance(p,dict) or set(p)!={'adapter','model','model_digest','rights_note','cost_units','max_output_tokens'}:raise ValueError()
            if p['adapter'] not in ('ollama','sd-webui','colibri','node6-text','node6-image','open-gen-ai','ffmpeg-composition') or not isinstance(p['model'],str) or not re.fullmatch('[A-Za-z0-9][A-Za-z0-9_./:-]{0,99}',p['model']):raise ValueError()
            if not isinstance(p['model_digest'],str) or not re.fullmatch('[a-f0-9]{64}',p['model_digest']):raise ValueError()
            if not isinstance(p['rights_note'],str) or not 1<=len(p['rights_note'])<=500 or any(ord(c)<32 for c in p['rights_note']):raise ValueError()
            if type(p['cost_units'])!=int or not 1<=p['cost_units']<=1000000 or type(p['max_output_tokens'])!=int or not 16<=p['max_output_tokens']<=1024:raise ValueError()
            result[key]={**p,'id':key,'configuration_digest':digest(p),'kinds':['VIDEO'] if p['adapter']=='ffmpeg-composition' else ['SCRIPT','COPY'] if p['adapter'] in ('ollama','colibri','node6-text') else ['IMAGE'],'remote_required':p['adapter'] in ('node6-text','node6-image','open-gen-ai'),'execution_allowed':remote_approved(scope,provider,key,digest(p)) if p['adapter'] in ('node6-text','node6-image','open-gen-ai') else True,'cost_basis':'OPERATOR_ESTIMATE','cost_currency':'LOCAL_CREDIT','rights_authenticity_verified':False}
        return result
    except (ValueError,TypeError,AttributeError):raise CRMError('GENERATION_CONFIGURATION_INVALID',503) from None

def _json(client,method,url,data=None,headers=None):
    try:
        with client.stream(method,url,json=data,headers={'Accept':'application/json',**(headers or {})}) as response:
            if response.status_code!=200:raise CRMError('GENERATION_PROVIDER_REJECTED',503)
            raw=bytearray()
            for chunk in response.iter_bytes():
                raw.extend(chunk)
                if len(raw)>MAX_RESPONSE:raise CRMError('GENERATION_PROVIDER_RESPONSE_LIMIT',503)
        value=json.loads(raw)
        if not isinstance(value,(dict,list)):raise ValueError()
        return value
    except CRMError:raise
    except (httpx.HTTPError,ValueError,TypeError,RecursionError):raise CRMError('GENERATION_PROVIDER_UNAVAILABLE_OR_INVALID',503) from None

def generate(job,client_factory=None):
    """Worker-only execution; callers cannot supply endpoint, model path, tool or shell command."""
    p=job['profile'];
    if p.get('remote_required') and not remote_approved(job['scope'],job.get('provider_ref'),p['id'],p['configuration_digest']):raise CRMError('GENERATION_REMOTE_APPROVAL_REQUIRED',503)
    prompt=PROMPT_PREFIX+('Formato: guion con escenas y narración.\n' if job['kind']=='SCRIPT' else '')+job['prompt']
    factory=client_factory or httpx.Client
    with factory(timeout=httpx.Timeout(180,connect=3),follow_redirects=False,trust_env=False) as client:
        if p['adapter']=='ollama':
            base=endpoint(p['adapter']);catalog=_json(client,'GET',base+'/api/tags')
            known=catalog.get('models',[]) if isinstance(catalog,dict) else []
            if not any(isinstance(x,dict) and x.get('name')==p['model'] and x.get('digest')==p['model_digest'] for x in known):raise CRMError('GENERATION_LOCAL_MODEL_NOT_QUALIFIED',503)
            value=_json(client,'POST',base+'/api/generate',{'model':p['model'],'prompt':prompt,'stream':False,'keep_alive':0,'options':{'num_predict':p['max_output_tokens'],'temperature':0.4}})
            if not isinstance(value,dict) or value.get('done') is not True or value.get('model')!=p['model'] or not isinstance(value.get('response'),str) or not value['response'].strip():raise CRMError('GENERATION_INVALID_TEXT_RESULT',503)
            data=value['response'].encode('utf-8')
            if len(data)>32768 or any(ord(c)<32 and c not in '\n\t\r' for c in value['response']):raise CRMError('GENERATION_INVALID_TEXT_RESULT',503)
            usage={k:value.get(k) for k in ('prompt_eval_count','eval_count')}
            if any(type(v)!=int or not 0<=v<=1000000 for v in usage.values()) or usage['eval_count']>p['max_output_tokens']:raise CRMError('GENERATION_INVALID_USAGE',503)
            # A model with the same name replaced during execution is not accepted.
            after=_json(client,'GET',base+'/api/tags')
            if not isinstance(after,dict) or not any(isinstance(x,dict) and x.get('name')==p['model'] and x.get('digest')==p['model_digest'] for x in after.get('models',[])):raise CRMError('GENERATION_LOCAL_MODEL_CHANGED',503)
            return data,'text/plain',{'adapter':p['adapter'],'model':p['model'],'model_digest':p['model_digest'],'model_digest_verification':'LOCAL_API_MATCH','usage':usage,'source_sha256':hashlib.sha256(data).hexdigest()}
        if p['adapter']=='colibri':
            base=endpoint(p['adapter']);headers=credentials(job);catalog=_json(client,'GET',base+'/v1/models',headers=headers)
            if not isinstance(catalog,dict) or not any(isinstance(x,dict) and x.get('id')==p['model'] for x in catalog.get('data',[])):raise CRMError('GENERATION_LOCAL_MODEL_NOT_QUALIFIED',503)
            value=_json(client,'POST',base+'/v1/chat/completions',{'model':p['model'],'messages':[{'role':'user','content':prompt}],'max_tokens':p['max_output_tokens'],'stream':False},headers)
            try:
                content=value['choices'][0]['message']['content'];usage=value['usage']
                if value.get('model')!=p['model'] or not isinstance(content,str) or not content.strip() or len(content.encode())>32768:raise ValueError()
                counts={k:usage[k] for k in ('prompt_tokens','completion_tokens')}
                if any(type(v)!=int or not 0<=v<=1000000 for v in counts.values()) or counts['completion_tokens']>p['max_output_tokens']:raise ValueError()
            except (KeyError,IndexError,TypeError,ValueError):raise CRMError('GENERATION_INVALID_TEXT_RESULT',503) from None
            data=content.encode();return data,'text/plain',{'adapter':p['adapter'],'model':p['model'],'model_digest':p['model_digest'],'model_digest_verification':'OPERATOR_DECLARATION','usage':counts,'source_sha256':hashlib.sha256(data).hexdigest()}
        if p['adapter'] in ('node6-text','node6-image'):
            base=endpoint(p['adapter']);headers=credentials(job)
            if not headers:raise CRMError('GENERATION_SECRET_BINDING_REQUIRED',503)
            state=_json(client,'GET',base+'/status',headers=headers);field='text_model' if p['adapter']=='node6-text' else 'image_model'
            if not isinstance(state,dict) or state.get(field)!=p['model']:raise CRMError('GENERATION_LOCAL_MODEL_NOT_QUALIFIED',503)
            value=_json(client,'POST',base+('/studio/script' if p['adapter']=='node6-text' else '/studio/image'),{'prompt':prompt,**({'provider':'gemini'} if p['adapter']=='node6-text' else {})},headers)
            if not isinstance(value,dict) or value.get('model')!=p['model'] or value.get('provider')!='gemini':raise CRMError('GENERATION_LOCAL_MODEL_CHANGED',503)
            trace={'adapter':p['adapter'],'model':p['model'],'model_digest':p['model_digest'],'model_digest_verification':'OPERATOR_DECLARATION','remote_provider':'gemini','usage':None}
            if p['adapter']=='node6-text':
                content=value.get('text')
                if not isinstance(content,str) or not content.strip() or len(content.encode())>32768:raise CRMError('GENERATION_INVALID_TEXT_RESULT',503)
                data=content.encode();return data,'text/plain',{**trace,'source_sha256':hashlib.sha256(data).hexdigest()}
            data,mime,info=_image_artifact(client,base,value.get('artifact_url'),headers);return data,mime,{**trace,**info}
        if p['adapter']=='open-gen-ai':
            base=endpoint(p['adapter']);headers=credentials(job);value=_json(client,'POST',base+'/api/generate/image',{'prompt':prompt,'model':p['model'],'format':'post_1_1','inquilino_id':job['scope']},headers)
            if not isinstance(value,dict) or value.get('model')!=p['model']:raise CRMError('GENERATION_LOCAL_MODEL_CHANGED',503)
            data,mime,info=_image_artifact(client,base,value.get('image_url'),headers);return data,mime,{**info,'adapter':p['adapter'],'model':p['model'],'model_digest':p['model_digest'],'model_digest_verification':'OPERATOR_DECLARATION','usage':None}
        if p['adapter']=='sd-webui':
            base=endpoint(p['adapter']);catalog=_json(client,'GET',base+'/sdapi/v1/sd-models')
            matches=[x for x in catalog if isinstance(x,dict) and x.get('model_name')==p['model'] and x.get('sha256')==p['model_digest']] if isinstance(catalog,list) else []
            if len(matches)!=1 or not isinstance(matches[0].get('title'),str) or len(matches[0]['title'])>200:raise CRMError('GENERATION_LOCAL_MODEL_NOT_QUALIFIED',503)
            value=_json(client,'POST',base+'/sdapi/v1/txt2img',{'prompt':prompt,'width':512,'height':512,'batch_size':1,'n_iter':1,'steps':20,'cfg_scale':7,'seed':-1,'override_settings':{'sd_model_checkpoint':matches[0]['title']},'override_settings_restore_afterwards':True,'send_images':True,'save_images':False})
            try:
                if not isinstance(value,dict) or not isinstance(value.get('images'),list) or len(value['images'])!=1 or not isinstance(value['images'][0],str):raise ValueError()
                info=json.loads(value['info']) if isinstance(value.get('info'),str) else value.get('info')
                if not isinstance(info,dict) or info.get('sd_model_hash') not in (p['model_digest'],p['model_digest'][:10]):raise ValueError()
                raw=base64.b64decode(value['images'][0],validate=True)
                data,mime,media=sanitize(raw,'image/png')
                if media['width']!=512 or media['height']!=512:raise ValueError()
            except (ValueError,KeyError,TypeError,CRMError):raise CRMError('GENERATION_INVALID_IMAGE_RESULT',503) from None
            return data,mime,{'adapter':p['adapter'],'model':p['model'],'model_digest':p['model_digest'],'usage':{'images':1,'steps':20},'source_sha256':hashlib.sha256(raw).hexdigest(),'media':media}
        raise CRMError('GENERATION_ADAPTER_UNAVAILABLE',503)
