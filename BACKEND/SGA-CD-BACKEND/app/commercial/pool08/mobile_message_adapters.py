"""Separate fixed-host adapters. This module never promotes acceptance to delivery."""
import json,os,re
import httpx
from .crm import CRMError
MAX_RESPONSE=65536
def credential(policy):
 raw=os.environ.get(policy['credential_env'],'')
 if not raw or len(raw)>4096 or any(ord(c)<32 for c in raw):raise CRMError('MOBILE_CREDENTIAL_REQUIRED',503)
 if policy['adapter'].startswith('twilio-'):
  try:
   value=json.loads(raw)
   if set(value)!={'account_sid','auth_token'} or not re.fullmatch('AC[0-9a-fA-F]{32}',value['account_sid']) or not isinstance(value['auth_token'],str) or not 20<=len(value['auth_token'])<=200 or any(ord(c)<33 for c in value['auth_token']):raise ValueError()
   return value
  except (ValueError,TypeError,KeyError):raise CRMError('MOBILE_CREDENTIAL_REQUIRED',503) from None
 if len(raw)<20 or any(ord(c)<33 for c in raw):raise CRMError('MOBILE_CREDENTIAL_REQUIRED',503)
 return raw

def sms_request(job,p,prepared,secret):
 if job['channel']!='SMS' or job['mode'] not in ('TEXT','TEXT_WITH_LINK'):raise CRMError('MOBILE_SMS_HAS_NO_ATTACHMENTS')
 return ('https://api.twilio.com/2010-04-01/Accounts/'+secret['account_sid']+'/Messages.json',{'data':{'To':job['phone'],'From':p['from_id'],'Body':prepared['body']},'auth':(secret['account_sid'],secret['auth_token'])})
def mms_request(job,p,prepared,secret):
 if job['channel']!='MMS' or job['mode']!='MULTIMEDIA' or not prepared['media']:raise CRMError('MOBILE_MULTIMEDIA_REQUIRED')
 return ('https://api.twilio.com/2010-04-01/Accounts/'+secret['account_sid']+'/Messages.json',{'data':{'To':job['phone'],'From':p['from_id'],'Body':prepared['body'],'MediaUrl':prepared['media']['url']},'auth':(secret['account_sid'],secret['auth_token'])})
def whatsapp_request(job,p,prepared,secret):
 if job['channel']!='WHATSAPP' or not prepared['media']:raise CRMError('MOBILE_MULTIMEDIA_REQUIRED')
 kind='image' if prepared['media']['kind']=='IMAGE' else 'video'
 data={'messaging_product':'whatsapp','to':job['phone'][1:],'type':'template','template':{'name':p['wa_template_name'],'language':{'code':p['wa_language']},'components':[{'type':'header','parameters':[{'type':kind,kind:{'link':prepared['media']['url']}}]},{'type':'body','parameters':[{'type':'text','text':prepared['body']}]}]}}
 return ('https://graph.facebook.com/v22.0/'+p['from_id']+'/messages',{'json':data,'headers':{'Authorization':'Bearer '+secret}})

def dispatch(job,policy,prepared,client_factory=None):
 if os.environ.get('COMMERCIAL_MOBILE_NETWORK_ENABLED')!='1':raise CRMError('MOBILE_NETWORK_DISABLED',503)
 secret=credential(policy);builder={'twilio-sms':sms_request,'twilio-mms':mms_request,'meta-whatsapp':whatsapp_request}.get(policy['adapter'])
 if not builder:raise CRMError('MOBILE_ADAPTER_REQUIRED',503)
 url,kwargs=builder(job,policy,prepared,secret)
 try:
  with (client_factory or httpx.Client)(timeout=httpx.Timeout(15,connect=3),follow_redirects=False,trust_env=False) as client:
   with client.stream('POST',url,**kwargs) as response:
    if 400<=response.status_code<500:return {'status':'REJECTED','provider_id':None}
    if response.status_code not in (200,201,202):return {'status':'UNCERTAIN','provider_id':None}
    raw=bytearray()
    for chunk in response.iter_bytes():
     raw.extend(chunk)
     if len(raw)>MAX_RESPONSE:return {'status':'UNCERTAIN','provider_id':None}
   value=json.loads(raw)
   if policy['adapter'].startswith('twilio-'):
    ref=value.get('sid')
    if not isinstance(ref,str) or not re.fullmatch('SM[0-9a-fA-F]{32}',ref):raise ValueError()
    if value.get('status') in ('failed','undelivered'):return {'status':'REJECTED','provider_id':ref}
   else:
    refs=value.get('messages');ref=refs[0]['id'] if isinstance(refs,list) and len(refs)==1 else None
    if not isinstance(ref,str) or not re.fullmatch(r'wamid\.[A-Za-z0-9_.=\-]{1,180}',ref):raise ValueError()
   return {'status':'ACCEPTED','provider_id':ref}
 except (httpx.HTTPError,ValueError,KeyError,TypeError,AttributeError):return {'status':'UNCERTAIN','provider_id':None}
