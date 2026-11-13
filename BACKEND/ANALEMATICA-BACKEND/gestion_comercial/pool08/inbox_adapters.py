"""Owned text reply protocols. No real send is exercised by automated tests.

Acceptance means a provider returned a bound message identifier, never delivery.
TikTok has no assumed universal DM/comment reply API: hand off instead.
"""
import os,json,re,base64
from email.message import EmailMessage
from email.policy import SMTP
import httpx
class ProtocolError(Exception):pass
def send(d,p,client_factory=None):
 unknown={'status':'UNCERTAIN','remote_id':None};token=os.environ.get(p['credential_env'],'')
 if not isinstance(token,str) or not 16<=len(token)<=4096 or any(ord(c)<33 or ord(c)>126 for c in token):return unknown
 try:
  with (client_factory or httpx.Client)(timeout=httpx.Timeout(15,connect=3),follow_redirects=False,trust_env=False,headers={'Authorization':'Bearer '+token}) as client:
   def call(method,url,**kwargs):
    with client.stream(method,url,**kwargs) as r:
     if not 200<=r.status_code<300:raise ProtocolError()
     raw=b''
     for part in r.iter_bytes():
      raw+=part
      if len(raw)>65536:raise ProtocolError()
     value=json.loads(raw)
     if not isinstance(value,dict):raise ProtocolError()
     return value
   def identifier(value,pattern=r'[A-Za-z0-9_@.+<>=:-]{1,200}'):
    if not isinstance(value,str) or not re.fullmatch(pattern,value):raise ProtocolError()
    return value
   channel=d['channel'];account=identifier(p['account_id']);sender=identifier(d['sender_ref']);thread=identifier(d['thread_ref']);body=d['reply']['text'];base='https://graph.facebook.com/v22.0/'
   if channel in ('FB_DM','FB_COMMENT','IG_COMMENT','IG_DM'):
    identifier(account,r'[0-9]{1,40}')
    if channel in ('IG_DM','IG_COMMENT'):
     owned=call('GET',base+'me/accounts',params={'fields':'id,tasks,instagram_business_account{id}'})
     if not any(v.get('id')==p['page_id'] and v.get('instagram_business_account',{}).get('id')==account and any(t in ('MANAGE','MESSAGING','MODERATE') for t in v.get('tasks',[])) for v in owned.get('data',[]) if isinstance(v,dict)):raise ProtocolError()
    elif call('GET',base+'me',params={'fields':'id'}).get('id')!=account:raise ProtocolError()
    if channel in ('FB_DM','IG_DM'):
     identifier(sender,r'[0-9]{1,40}')
     if thread!=sender:raise ProtocolError()
     payload={'recipient':{'id':sender},'message':{'text':body}}
     if channel=='FB_DM':payload['messaging_type']='RESPONSE'
     ack=call('POST',base+account+'/messages',json=payload)
     if ack.get('recipient_id')!=sender:raise ProtocolError()
     mid=identifier(ack.get('message_id'))
    else:
     identifier(thread,r'[0-9_]{1,100}');parent=call('GET',base+thread,params={'fields':'id,from,media' if channel=='IG_COMMENT' else 'id,from,object'})
     if parent.get('id')!=thread:raise ProtocolError()
     if channel=='IG_COMMENT':
      media_id=identifier(parent.get('media',{}).get('id'),r'[0-9]{1,40}');owner=call('GET',base+media_id,params={'fields':'id,owner'})
      if owner.get('owner',{}).get('id')!=account:raise ProtocolError()
     else:
      # A public comment is not automatically owned by this Page. Check the
      # parent post's owner before posting; the comment author is the customer.
      post_id=identifier(parent.get('object',{}).get('id'),r'[0-9_]{1,100}');owner=call('GET',base+post_id,params={'fields':'id,from'})
      if owner.get('from',{}).get('id')!=account:raise ProtocolError()
     ack=call('POST',base+thread+('/replies' if channel=='IG_COMMENT' else '/comments'),data={'message':body});mid=identifier(ack.get('id'))
     # Read the new object to bind acceptance to the requested parent.
     proof=call('GET',base+mid,params={'fields':'id,parent,from,text' if channel=='IG_COMMENT' else 'id,parent,from,message'})
     if proof.get('id')!=mid or proof.get('parent',{}).get('id')!=thread or proof.get('from',{}).get('id')!=account:raise ProtocolError()
   elif channel=='WHATSAPP':
    identifier(account,r'[0-9]{1,40}');identifier(sender,r'[0-9]{7,15}')
    if call('GET',base+account,params={'fields':'id,display_phone_number'}).get('id')!=account:raise ProtocolError()
    anchor=identifier(d['reply']['anchor_id']);ack=call('POST',base+account+'/messages',json={'messaging_product':'whatsapp','recipient_type':'individual','to':sender,'context':{'message_id':anchor},'type':'text','text':{'body':body,'preview_url':False}})
    if not any(v.get('wa_id')==sender for v in ack.get('contacts',[]) if isinstance(v,dict)):raise ProtocolError()
    mid=identifier(ack['messages'][0]['id'])
   elif channel=='EMAIL':
    base='https://gmail.googleapis.com/gmail/v1/users/me/'
    if call('GET',base+'profile').get('emailAddress','').lower()!=account.lower():raise ProtocolError()
    # Use the API's existing thread and its actual headers, not a browser-supplied
    # recipient/Reply-To. Reject ambiguous group replies and header injection.
    remote=call('GET',base+'threads/'+thread,params={'format':'metadata','metadataHeaders':['From','Message-ID','Subject']})
    original=next((v for v in remote.get('messages',[]) if v.get('id')==d['reply']['anchor_id']),None)
    if not original or remote.get('id')!=thread:raise ProtocolError()
    headers={h['name'].lower():h['value'] for h in original.get('payload',{}).get('headers',[]) if isinstance(h,dict) and 'name' in h and 'value' in h}
    from email.utils import parseaddr
    if parseaddr(headers.get('from',''))[1].lower()!=sender.lower():raise ProtocolError()
    anchor=next(m for m in d['messages'] if m['direction']=='IN' and m['remote_id']==d['reply']['anchor_id'])
    if headers.get('message-id')!=anchor['reply_to_ref']:raise ProtocolError()
    subject=headers.get('subject','')
    if len(subject)>200 or any(c in subject for c in '\r\n'):raise ProtocolError()
    message=EmailMessage(policy=SMTP);message['From']=account;message['To']=sender;message['Subject']=subject if subject.lower().startswith('re:') else 'Re: '+subject;message['In-Reply-To']=anchor['reply_to_ref'];message['References']=anchor['reply_to_ref'];message.set_content(body)
    ack=call('POST',base+'messages/send',json={'threadId':thread,'raw':base64.urlsafe_b64encode(message.as_bytes()).decode()})
    if ack.get('threadId')!=thread:raise ProtocolError()
    mid=identifier(ack.get('id'))
   elif channel=='YOUTUBE_COMMENT':
    base='https://www.googleapis.com/youtube/v3/';identifier(account,r'UC[A-Za-z0-9_-]{22}')
    owned=call('GET',base+'channels',params={'part':'id','mine':'true'})
    if not any(v.get('id')==account for v in owned.get('items',[]) if isinstance(v,dict)):raise ProtocolError()
    parent=call('GET',base+'comments',params={'part':'snippet','id':thread})
    if not any(v.get('id')==thread and v.get('snippet',{}).get('channelId')==account for v in parent.get('items',[]) if isinstance(v,dict)):raise ProtocolError()
    ack=call('POST',base+'comments',params={'part':'snippet'},json={'snippet':{'parentId':thread,'textOriginal':body}})
    if ack.get('snippet',{}).get('parentId')!=thread or ack.get('snippet',{}).get('authorChannelId',{}).get('value')!=account:raise ProtocolError()
    mid=identifier(ack.get('id'))
   else:raise ProtocolError()
   return {'status':'ACCEPTED','remote_id':mid}
 except (httpx.HTTPError,ProtocolError,ValueError,KeyError,TypeError,AttributeError,IndexError,StopIteration):return unknown
