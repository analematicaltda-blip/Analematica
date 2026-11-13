"""Provider-specific inbound boundaries; never sends replies.

Meta verifies raw-body HMAC before parsing. Gmail/YouTube are explicit, bounded
OAuth reads from fixed hosts. Neither method proves a person's legal identity.
"""
import os,json,re,hmac,hashlib,uuid,base64
from datetime import datetime,timezone
from email.utils import parseaddr
from .inbox import CRMError,digest,remote_ref
MAX_RAW=8192

def normalized(engine,account,channel,thread,message,sender,body,when,reply=None,subject='Consulta recibida'):
 event={'event_id':str(uuid.uuid5(uuid.NAMESPACE_URL,engine.key()+':'+account+':'+channel+':'+message)),'account_ref':account,'channel':channel,'thread_ref':str(thread),'message_ref':str(message),'sender_ref':str(sender),'body':body,'occurred_at':when,'reply_to_ref':reply,'subject':subject}
 p=engine.profile(account,channel);secret=os.environ.get(p['ingress_key_env'],'')
 if not 32<=len(secret)<=256:raise CRMError('INBOX_INGRESS_KEY_REQUIRED',503)
 signature=hmac.new(secret.encode(),digest({'key':engine.key(),'event':event}).encode(),hashlib.sha256).hexdigest()
 return engine.ingest(event,signature)

def meta(engine,account,raw,signature):
 engine.authority()
 if not isinstance(raw,bytes) or not 1<=len(raw)<=MAX_RAW:raise CRMError('INBOX_NATIVE_BODY_LIMIT',413)
 try:
  reference=json.loads(os.environ.get('COMMERCIAL_INBOX_META_KEYS','{}'))[engine.key()][account]
  if not isinstance(reference,str) or not re.fullmatch('COMMERCIAL_INBOX_NATIVE_[A-Z0-9_]{1,60}',reference):raise ValueError()
  secret=os.environ[reference]
  if not 32<=len(secret)<=256:raise ValueError()
 except (ValueError,TypeError,KeyError):raise CRMError('INBOX_NATIVE_KEY_REQUIRED',503) from None
 expected='sha256='+hmac.new(secret.encode(),raw,hashlib.sha256).hexdigest()
 if not isinstance(signature,str) or not re.fullmatch('sha256=[a-f0-9]{64}',signature) or not hmac.compare_digest(signature,expected):raise CRMError('INBOX_NATIVE_SIGNATURE_REQUIRED',403)
 def unique(pairs):
  values={}
  for k,v in pairs:
   if k in values:raise ValueError()
   values[k]=v
  return values
 try:
  packet=json.loads(raw,object_pairs_hook=unique);entries=packet['entry'];object_type=packet['object'];results=[]
  if not isinstance(entries,list) or len(entries)!=1:raise ValueError()
  entry=entries[0];native_id=str(entry['id'])
  if object_type in ('page','instagram') and 'messaging' in entry:
   channel='FB_DM' if object_type=='page' else 'IG_DM';p=engine.profile(account,channel);messages=entry['messaging']
   if native_id!=p['account_id'] or not isinstance(messages,list) or len(messages)!=1:raise ValueError()
   m=messages[0];sender=str(m['sender']['id']);message=m['message']
   if str(m['recipient']['id'])!=native_id or message.get('is_echo') or 'text' not in message:raise ValueError()
   when=datetime.fromtimestamp(int(m['timestamp'])/1000,timezone.utc).isoformat();results.append(normalized(engine,account,channel,sender,message['mid'],sender,message['text'],when))
  else:
   changes=entry['changes']
   if not isinstance(changes,list) or len(changes)!=1:raise ValueError()
   change=changes[0];value=change['value'];field=change['field']
   if object_type=='whatsapp_business_account' and field=='messages':
    channel='WHATSAPP';p=engine.profile(account,channel)
    if str(value['metadata']['phone_number_id'])!=p['account_id'] or len(value['messages'])!=1:raise ValueError()
    m=value['messages'][0]
    if m['type']!='text':raise ValueError()
    sender=str(m['from']);when=datetime.fromtimestamp(int(m['timestamp']),timezone.utc).isoformat();results.append(normalized(engine,account,channel,sender,m['id'],sender,m['text']['body'],when))
   elif object_type=='page' and field=='feed' and value.get('item')=='comment' and value.get('verb')=='add':
    channel='FB_COMMENT';p=engine.profile(account,channel)
    if native_id!=p['account_id'] or not str(value['post_id']).startswith(native_id+'_'):raise ValueError()
    when=datetime.fromtimestamp(int(value['created_time']),timezone.utc).isoformat();results.append(normalized(engine,account,channel,value['comment_id'],value['comment_id'],value['from']['id'],value['message'],when))
   elif object_type=='instagram' and field=='comments':
    channel='IG_COMMENT';p=engine.profile(account,channel)
    if native_id!=p['account_id']:raise ValueError()
    when=datetime.fromtimestamp(int(entry['time']),timezone.utc).isoformat();results.append(normalized(engine,account,channel,value['id'],value['id'],value['from']['id'],value['text'],when))
   else:raise ValueError()
  return {'receipts':results,'raw_body_sha256':hashlib.sha256(raw).hexdigest(),'native_signature_checked':True,'real_provider_qualified':False,'replies_sent':False}
 except (ValueError,TypeError,KeyError,IndexError,AttributeError,OverflowError,OSError):raise CRMError('INBOX_NATIVE_TEXT_EVENT_UNSUPPORTED') from None

def sync(engine,account,channel,client_factory=None):
 engine.authority(channel)
 if channel not in ('EMAIL','YOUTUBE_COMMENT'):raise CRMError('INBOX_SOURCE_POLL_UNSUPPORTED',409)
 if os.environ.get('COMMERCIAL_INBOX_INGRESS_NETWORK_ENABLED')!='1':raise CRMError('INBOX_SOURCE_NETWORK_DISABLED',503)
 p=engine.profile(account,channel);token=os.environ.get(p['credential_env'],'')
 if not 16<=len(token)<=4096 or any(ord(c)<33 or ord(c)>126 for c in token):raise CRMError('INBOX_CREDENTIAL_REQUIRED',503)
 import httpx
 try:
  with (client_factory or httpx.Client)(timeout=httpx.Timeout(15,connect=3),follow_redirects=False,trust_env=False,headers={'Authorization':'Bearer '+token}) as client:
   def get(url,params=None):
    with client.stream('GET',url,params=params) as response:
     if response.status_code!=200:raise ValueError()
     raw=b''
     for part in response.iter_bytes():
      raw+=part
      if len(raw)>65536:raise ValueError()
     value=json.loads(raw)
     if not isinstance(value,dict):raise ValueError()
     return value
   results=[];skipped=0
   if channel=='EMAIL':
    base='https://gmail.googleapis.com/gmail/v1/users/me/'
    if get(base+'profile').get('emailAddress','').lower()!=p['account_id'].lower():raise ValueError()
    listing=get(base+'messages',{'labelIds':'INBOX','maxResults':10});items=listing.get('messages',[])
    if not isinstance(items,list) or len(items)>10:raise ValueError()
    for item in items:
     mid=remote_ref(item['id']);message=get(base+'messages/'+mid,{'format':'full'})
     if message.get('id')!=mid:raise ValueError()
     headers={h['name'].lower():h['value'] for h in message['payload'].get('headers',[])};sender=parseaddr(headers.get('from',''))[1];subject=headers.get('subject','')
     if any(c in subject for c in '\r\n') or len(subject)>200:raise ValueError()
     def plain(part,depth=0):
      if depth>3:raise ValueError()
      if part.get('mimeType')=='text/plain' and not part.get('filename'):
       encoded=part.get('body',{}).get('data','')
       if not re.fullmatch('[A-Za-z0-9_=-]*',encoded):raise ValueError()
       return base64.urlsafe_b64decode(encoded+'='*((-len(encoded))%4)).decode('utf-8')
      parts=part.get('parts',[])
      if not isinstance(parts,list) or len(parts)>10:raise ValueError()
      for sub in parts:
       found=plain(sub,depth+1)
       if found is not None:return found
      return None
     body=plain(message['payload'])
     if not body or len(body)>4000:skipped+=1;continue
     when=datetime.fromtimestamp(int(message['internalDate'])/1000,timezone.utc).isoformat();results.append(normalized(engine,account,channel,message['threadId'],mid,sender,body,when,headers.get('message-id'),subject))
   else:
    base='https://www.googleapis.com/youtube/v3/'
    if not any(v.get('id')==p['account_id'] for v in get(base+'channels',{'part':'id','mine':'true'}).get('items',[])):raise ValueError()
    listing=get(base+'commentThreads',{'part':'snippet','allThreadsRelatedToChannelId':p['account_id'],'maxResults':10,'order':'time','textFormat':'plainText'});items=listing.get('items',[])
    if not isinstance(items,list) or len(items)>10:raise ValueError()
    for item in items:
     snippet=item['snippet'];comment=snippet['topLevelComment'];content=comment['snippet']
     if snippet.get('channelId')!=p['account_id']:raise ValueError()
     sender=content.get('authorChannelId',{}).get('value')
     if not sender:skipped+=1;continue
     results.append(normalized(engine,account,channel,comment['id'],comment['id'],sender,content['textOriginal'],content['publishedAt'],subject='Consulta YouTube'))
   return {'receipts':results,'skipped_needs_review':skipped,'more_available':bool(listing.get('nextPageToken')),'full_mailbox_or_history_synced':False,'replies_sent':False,'real_provider_qualified':False}
 except (httpx.HTTPError,ValueError,TypeError,KeyError,AttributeError,OverflowError,OSError):raise CRMError('INBOX_SOURCE_REVIEW_REQUIRED',502) from None
