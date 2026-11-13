"""Official outbound adapters. Provider acceptance is distinct from delivery/read status.
No browser credentials, global-channel fallback, unbounded polling or automatic re-send.
"""
import base64
from email.message import EmailMessage
import hashlib
import hmac
import json
import secrets
import time
from urllib.parse import quote,urlencode,urlparse,parse_qsl
import requests
from .engine import WorkerError

PROVIDERS={'youtube','instagram','facebook','whatsapp','x','tiktok','gmail'}
class Rejected(Exception):
    def __init__(self,retry_after=0):self.retry_after=retry_after

def oauth1(method,url,credentials,data=None):
    enc=lambda value:quote(str(value),safe='~-._')
    values={'oauth_consumer_key':credentials['consumer_key'],'oauth_token':credentials['access_token'],'oauth_nonce':secrets.token_hex(16),'oauth_timestamp':str(int(time.time())),'oauth_signature_method':'HMAC-SHA1','oauth_version':'1.0'}
    parameters=list(values.items())+parse_qsl(urlparse(url).query)+(list(data.items()) if data else [])
    normalized='&'.join(k+'='+v for k,v in sorted((enc(k),enc(v)) for k,v in parameters))
    origin=urlparse(url);base=origin.scheme+'://'+origin.netloc+origin.path
    signature='&'.join([method.upper(),enc(base),enc(normalized)])
    key=enc(credentials['consumer_secret'])+'&'+enc(credentials['access_secret'])
    values['oauth_signature']=base64.b64encode(hmac.new(key.encode(),signature.encode(),hashlib.sha1).digest()).decode()
    return 'OAuth '+', '.join(enc(k)+'="'+enc(v)+'"' for k,v in sorted(values.items()))

class Social:
    def __init__(self,engine):self.engine=engine
    def request(self,method,url,credentials=None,oauth=False,**kwargs):
        headers=kwargs.pop('headers',{})
        if oauth:headers['Authorization']=oauth1(method,url,credentials,kwargs.get('data') if not kwargs.get('files') else None)
        elif credentials and credentials.get('access_token'):headers['Authorization']='Bearer '+credentials['access_token']
        response=self.engine.client.request(method,url,headers=headers,timeout=(10,90),allow_redirects=False,**kwargs)
        if response.status_code==429:
            try:wait=max(30,min(3600,int(response.headers.get('Retry-After','60'))))
            except (TypeError,ValueError):wait=60
            raise Rejected(wait)
        if 400<=response.status_code<500:raise Rejected()
        if not 200<=response.status_code<300:raise requests.RequestException('Provider outcome not confirmed')
        # Some successful append/upload endpoints deliberately return no JSON body.
        if response.status_code==204 or not response.content:return {}
        value=response.json()
        if not isinstance(value,dict):raise ValueError()
        if isinstance(value.get('error'),dict) and value['error'].get('code') not in [None,'ok',0]:raise Rejected()
        return value
    def graph(self,credentials,object_id):return 'https://graph.facebook.com/'+credentials.get('api_version','v23.0')+'/'+object_id
    def deliver(self,provider,filename,credentials,title,description,recipient='',state=None,options=None,public_video_url='',unsubscribe_url=''):
        if provider not in PROVIDERS-{'youtube'}:raise WorkerError('Proveedor no disponible en este adaptador.',400)
        file=self.engine.artifact(filename)
        if file.suffix!='.mp4' or file.stat().st_size>40*1024*1024:raise WorkerError('Video no compatible con esta demo.',422)
        state=dict(state or {});options=options or {}
        try:
            result=getattr(self,provider)(file,credentials,title,description,recipient,state,options,public_video_url,unsubscribe_url)
            return {**result,'provider_state':state}
        except Rejected as error:
            return {'outcome':'rejected','retry_after':0 if (provider=='x' and state.get('media_id') and not state.get('upload_complete')) or (provider=='tiktok' and state.get('publish_id') and not state.get('uploaded')) else error.retry_after,'provider_state':state,'detail':'La plataforma rechazó la solicitud. Revisa permisos, formato y cuota.'}
        except (requests.RequestException,ValueError,KeyError,IndexError,TypeError,OSError):
            return {'outcome':'unknown','provider_state':state,'detail':'No se pudo confirmar el resultado; no se repetirá el envío automáticamente.'}
    def instagram(self,file,c,title,description,recipient,state,options,public_url,unsubscribe):
        if not public_url.startswith('https://'):raise WorkerError('Instagram requiere una URL HTTPS pública del video adaptado.',409)
        if not state.get('container_id'):
            result=self.request('POST',self.graph(c,c['account_id']+'/media'),c,data={'media_type':'REELS','video_url':public_url,'caption':title+'\n'+description,'share_to_feed':'true'})
            state['container_id']=result['id'];return {'outcome':'pending','remote_id':result['id']}
        result=self.request('GET',self.graph(c,state['container_id']),c,params={'fields':'status_code'})
        if result.get('status_code') in ['ERROR','EXPIRED']:return {'outcome':'rejected','detail':'Instagram no pudo procesar el video.'}
        if result.get('status_code')!='FINISHED':return {'outcome':'pending','remote_id':state['container_id']}
        result=self.request('POST',self.graph(c,c['account_id']+'/media_publish'),c,data={'creation_id':state['container_id']})
        return {'outcome':'published','remote_id':result['id']}
    def facebook(self,file,c,title,description,recipient,state,options,public_url,unsubscribe):
        if not state.get('video_id'):
            with file.open('rb') as stream:result=self.request('POST','https://graph-video.facebook.com/'+c.get('api_version','v23.0')+'/'+c['page_id']+'/videos',c,data={'title':title,'description':description,'published':'true'},files={'source':(file.name,stream,'video/mp4')})
            state['video_id']=result['id'];return {'outcome':'pending','remote_id':result['id']}
        result=self.request('GET',self.graph(c,state['video_id']),c,params={'fields':'status'})
        status=result.get('status',{}).get('video_status')
        if status=='error':return {'outcome':'rejected','detail':'Facebook no pudo procesar el video.'}
        return {'outcome':'published' if status=='ready' else 'pending','remote_id':state['video_id']}
    def whatsapp(self,file,c,title,description,recipient,state,options,public_url,unsubscribe):
        if file.stat().st_size>15*1024*1024:raise WorkerError('Adapta el video para WhatsApp (hasta 15 MB en esta demo).',422)
        if not state.get('media_id'):
            with file.open('rb') as stream:result=self.request('POST',self.graph(c,c['phone_number_id']+'/media'),c,data={'messaging_product':'whatsapp','type':'video/mp4'},files={'file':(file.name,stream,'video/mp4')})
            state['media_id']=result['id']
        components=[{'type':'header','parameters':[{'type':'video','video':{'id':state['media_id']}}]}]
        variables=options.get('template_variables',[])
        if variables:components.append({'type':'body','parameters':[{'type':'text','text':value} for value in variables]})
        result=self.request('POST',self.graph(c,c['phone_number_id']+'/messages'),c,json={'messaging_product':'whatsapp','to':recipient.lstrip('+'),'type':'template','template':{'name':options['template_name'],'language':{'code':options.get('template_language','es')},'components':components}})
        return {'outcome':'accepted','remote_id':result['messages'][0]['id'],'detail':'Aceptado por WhatsApp; la entrega requiere confirmación por webhook.'}
    def gmail(self,file,c,title,description,recipient,state,options,public_url,unsubscribe):
        if file.stat().st_size>15*1024*1024:raise WorkerError('Adapta el video para Gmail (hasta 15 MB adjuntos).',422)
        auth=self.request('POST','https://oauth2.googleapis.com/token',data={'grant_type':'refresh_token','client_id':c['client_id'],'client_secret':c['client_secret'],'refresh_token':c['refresh_token']})
        auth={'access_token':auth['access_token']}
        profile={'emailAddress':c['sender_email']}
        mail=EmailMessage();mail['From']=profile['emailAddress'];mail['To']=recipient;mail['Subject']=title
        if unsubscribe:
            mail['List-Unsubscribe']='<'+unsubscribe+'>';mail['List-Unsubscribe-Post']='List-Unsubscribe=One-Click'
        else:mail['List-Unsubscribe']='<mailto:'+profile['emailAddress']+'?subject=BAJA>'
        mail.set_content(description+'\n\n'+('Dejar de recibir estos mensajes: '+unsubscribe if unsubscribe else 'Para dejar de recibir estos mensajes, responde BAJA.'))
        mail.add_attachment(file.read_bytes(),maintype='video',subtype='mp4',filename='video-sgacd.mp4')
        result=self.request('POST','https://gmail.googleapis.com/gmail/v1/users/me/messages/send',auth,json={'raw':base64.urlsafe_b64encode(mail.as_bytes()).decode()})
        return {'outcome':'accepted','remote_id':result['id'],'detail':'Aceptado por Gmail; no confirma lectura ni entrega al destinatario.'}
    def x(self,file,c,title,description,recipient,state,options,public_url,unsubscribe):
        upload='https://upload.twitter.com/1.1/media/upload.json'
        if not state.get('media_id'):
            result=self.request('POST',upload,c,oauth=True,data={'command':'INIT','total_bytes':str(file.stat().st_size),'media_type':'video/mp4','media_category':'tweet_video'})
            state['media_id']=result['media_id_string']
            with file.open('rb') as stream:
                index=0
                while chunk:=stream.read(4*1024*1024):
                    self.request('POST',upload,c,oauth=True,data={'command':'APPEND','media_id':state['media_id'],'segment_index':str(index)},files={'media':('chunk',chunk,'application/octet-stream')});index+=1
            result=self.request('POST',upload,c,oauth=True,data={'command':'FINALIZE','media_id':state['media_id']});state['upload_complete']=True
        else:
            if not state.get('upload_complete'):raise WorkerError('Revisa el procesamiento incompleto de X antes de crear otro envío.',409)
            result=self.request('GET',upload+'?'+urlencode({'command':'STATUS','media_id':state['media_id']}),c,oauth=True)
        progress=result.get('processing_info',{}).get('state')
        if progress=='failed':return {'outcome':'rejected','detail':'X no pudo procesar el video.'}
        if progress in ['pending','in_progress']:return {'outcome':'pending','remote_id':state['media_id']}
        text=options.get('text',(title+'\n'+description).strip())
        if len(text)>280:raise WorkerError('Prepara el texto de X con hasta 280 caracteres.',422)
        result=self.request('POST','https://api.x.com/2/tweets',c,oauth=True,json={'text':text,'media':{'media_ids':[state['media_id']]}})
        return {'outcome':'published','remote_id':result['data']['id']}
    def tiktok(self,file,c,title,description,recipient,state,options,public_url,unsubscribe):
        base='https://open.tiktokapis.com/v2/'
        if state.get('publish_id'):
            result=self.request('POST',base+'post/publish/status/fetch/',c,json={'publish_id':state['publish_id']})['data'];status=result.get('status')
            if status=='FAILED':return {'outcome':'rejected','detail':'TikTok no pudo completar la publicación.'}
            return {'outcome':'published' if status=='PUBLISH_COMPLETE' else 'pending','remote_id':state['publish_id']}
        creator=self.request('POST',base+'post/publish/creator_info/query/',c,json={})['data']
        privacy=options.get('privacy','SELF_ONLY')
        if privacy not in creator.get('privacy_level_options',[]):raise WorkerError('La privacidad seleccionada no está autorizada para este creador de TikTok.',409)
        if creator.get('comment_disabled') is True:disable_comment=True
        else:disable_comment=bool(options.get('disable_comment',True))
        size=file.stat().st_size
        # Reel demo <=40 MB; one chunk is within TikTok's single-chunk ceiling.
        result=self.request('POST',base+'post/publish/video/init/',c,json={'post_info':{'title':(title+'\n'+description)[:2200],'privacy_level':privacy,'disable_duet':True,'disable_stitch':True,'disable_comment':disable_comment,'is_aigc':bool(options.get('is_aigc',False))},'source_info':{'source':'FILE_UPLOAD','video_size':size,'chunk_size':size,'total_chunk_count':1}})['data']
        url=result['upload_url'];parsed=urlparse(url)
        if parsed.scheme!='https' or not parsed.hostname or not parsed.hostname.endswith('.tiktokapis.com') or parsed.username or parsed.port not in [None,443]:raise ValueError()
        state['publish_id']=result['publish_id']
        with file.open('rb') as stream:self.request('PUT',url,headers={'Content-Type':'video/mp4','Content-Length':str(size),'Content-Range':f'bytes 0-{size-1}/{size}'},data=stream)
        state['uploaded']=True
        return {'outcome':'pending','remote_id':state['publish_id']}
