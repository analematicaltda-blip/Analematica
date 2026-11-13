"""Fixed-host provider protocols. Tests inject MockTransport, never real accounts.

Each call performs at most one mutation. A persisted container/upload identifier is
required before the next stage. HTTP success alone never establishes publication.
OAuth provisioning, provider review and real-account acceptance are external gates.
"""
import json,os,re,uuid
import httpx

def result(status,remote_id=None,container_id=None,proof=None):return dict(status=status,remote_id=remote_id,container_id=container_id,proof=proof)
class ProtocolError(Exception):pass

def step(d,p,media_url,raw=None,client_factory=None):
 mutation=d['claimed_from'] in ('SCHEDULED','READY_TO_PUBLISH');fallback='UNCERTAIN' if mutation else 'REMOTE_REVIEW'
 credential=os.environ.get(p['credential_env'],'')
 if not isinstance(credential,str) or not 16<=len(credential)<=4096 or any(ord(c)<33 or ord(c)>126 for c in credential):return result(fallback)
 # Never follow redirects, inherit proxies, expose credentials in query strings,
 # log response bodies or retry mutation requests after a network exception.
 try:
  with (client_factory or httpx.Client)(timeout=httpx.Timeout(15,connect=3),follow_redirects=False,trust_env=False,headers={'Authorization':'Bearer '+credential}) as client:
   def call(method,url,**kwargs):
    # All URLs below are built exclusively from fixed hosts and validated IDs.
    with client.stream(method,url,**kwargs) as response:
     if response.status_code<200 or response.status_code>=300:raise ProtocolError()
     content=b''
     for chunk in response.iter_bytes():
      content+=chunk
      if len(content)>65536:raise ProtocolError()
     try:value=json.loads(content)
     except (ValueError,UnicodeError):raise ProtocolError() from None
     if not isinstance(value,dict):raise ProtocolError()
     return value
   def identifier(value,pattern=r'[A-Za-z0-9_-]{1,200}'):
    if not isinstance(value,str) or not re.fullmatch(pattern,value):raise ProtocolError()
    return value
   account=p['account_id'];fmt=d['format'];stage=d['claimed_from'];remote=d.get('remote_id');container=d.get('container_id')
   def confirmed(remote_id,extra=None):return result('REMOTE_PRIVATE' if d['visibility']=='PRIVATE' else 'PUBLISHED',remote_id,proof={'basis':'PROVIDER_READ','account_id':account,'remote_id':remote_id,'visibility':d['visibility'],**(extra or {})})
   if fmt=='FACEBOOK_PHOTO':
    identifier(account,r'[0-9]{1,40}');base='https://graph.facebook.com/v22.0/'
    owner=call('GET',base+'me',params={'fields':'id'})
    if owner.get('id')!=account:raise ProtocolError()
    if stage=='SCHEDULED':
     ack=call('POST',base+account+'/photos',data={'url':media_url,'caption':d['caption'],'published':'true'})
     identifier(ack.get('id'),r'[0-9]{1,40}');post=identifier(ack.get('post_id'),r'[0-9]{1,40}_[0-9]{1,40}')
     if not post.startswith(account+'_'):raise ProtocolError()
     return result('VERIFY',post)
    identifier(remote,r'[0-9]{1,40}_[0-9]{1,40}');value=call('GET',base+remote,params={'fields':'id,from,is_published'})
    if value.get('id')==remote and value.get('from',{}).get('id')==account and value.get('is_published') is True:return confirmed(remote)
    return result('VERIFY')
   if fmt=='INSTAGRAM_REEL':
    identifier(account,r'[0-9]{1,40}');base='https://graph.facebook.com/v22.0/'
    owned=call('GET',base+'me/accounts',params={'fields':'id,tasks,instagram_business_account{id}'})
    pages=owned.get('data',[])
    if not isinstance(pages,list) or not any(isinstance(v,dict) and v.get('id')==p['page_id'] and v.get('instagram_business_account',{}).get('id')==account and any(t in ('CREATE_CONTENT','MANAGE') for t in v.get('tasks',[])) for v in pages):raise ProtocolError()
    if stage=='SCHEDULED':
     ack=call('POST',base+account+'/media',data={'media_type':'REELS','video_url':media_url,'caption':d['caption'],'share_to_feed':'true'})
     return result('WAIT_CONTAINER',container_id=identifier(ack.get('id'),r'[0-9]{1,40}'))
    if stage=='READY_TO_PUBLISH':
     identifier(container,r'[0-9]{1,40}');ack=call('POST',base+account+'/media_publish',data={'creation_id':container});return result('VERIFY',identifier(ack.get('id'),r'[0-9]{1,40}'))
    if stage=='WAIT_CONTAINER':
     identifier(container,r'[0-9]{1,40}');value=call('GET',base+container,params={'fields':'id,status_code'})
     if value.get('id')!=container:raise ProtocolError()
     state=value.get('status_code')
     return result('READY_TO_PUBLISH' if state=='FINISHED' else 'FAILED' if state in ('ERROR','EXPIRED') else 'WAIT_CONTAINER')
    identifier(remote,r'[0-9]{1,40}');value=call('GET',base+remote,params={'fields':'id,owner,media_type,media_product_type,permalink'})
    if value.get('id')==remote and value.get('owner',{}).get('id')==account and value.get('media_type')=='VIDEO' and value.get('media_product_type')=='REELS' and isinstance(value.get('permalink'),str) and value['permalink'].startswith('https://www.instagram.com/'):return confirmed(remote)
    return result('VERIFY')
   if fmt=='YOUTUBE_VIDEO':
    identifier(account,r'UC[A-Za-z0-9_-]{22}');base='https://www.googleapis.com/youtube/v3/'
    owner=call('GET',base+'channels',params={'part':'id','mine':'true'})
    if not any(isinstance(v,dict) and v.get('id')==account for v in owner.get('items',[])):raise ProtocolError()
    if stage=='SCHEDULED':
     if not isinstance(raw,bytes) or not 1<=len(raw)<=16777216:raise ProtocolError()
     privacy={'PUBLIC':'public','PRIVATE':'private','UNLISTED':'unlisted'}[d['visibility']];boundary='pool08_'+uuid.uuid4().hex
     metadata=json.dumps({'snippet':{'title':d['title'],'description':d['caption']},'status':{'privacyStatus':privacy}},ensure_ascii=False).encode()
     content=b'--'+boundary.encode()+b'\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n'+metadata+b'\r\n--'+boundary.encode()+b'\r\nContent-Type: video/mp4\r\n\r\n'+raw+b'\r\n--'+boundary.encode()+b'--\r\n'
     ack=call('POST','https://www.googleapis.com/upload/youtube/v3/videos',params={'part':'snippet,status','uploadType':'multipart'},content=content,headers={'Content-Type':'multipart/related; boundary='+boundary})
     return result('VERIFY',identifier(ack.get('id'),r'[A-Za-z0-9_-]{11}'))
    identifier(remote,r'[A-Za-z0-9_-]{11}');value=call('GET',base+'videos',params={'part':'snippet,status,processingDetails','id':remote})
    for v in value.get('items',[]):
     if v.get('id')==remote and v.get('snippet',{}).get('channelId')==account:
      status=v.get('status',{});processing=v.get('processingDetails',{}).get('processingStatus')
      if status.get('uploadStatus') in ('rejected','deleted','failed') or processing in ('failed','terminated'):return result('FAILED')
      if status.get('uploadStatus')=='processed' and processing=='succeeded' and status.get('privacyStatus')==d['visibility'].lower():return confirmed(remote)
    return result('VERIFY')
   if fmt=='TIKTOK_VIDEO':
    base='https://open.tiktokapis.com/v2/'
    def tk(method,path,**kwargs):
     value=call(method,base+path,**kwargs)
     if value.get('error',{}).get('code')!='ok' or not isinstance(value.get('data'),dict):raise ProtocolError()
     return value['data']
    owner=tk('GET','user/info/',params={'fields':'open_id,display_name'})
    if owner.get('user',{}).get('open_id')!=account:raise ProtocolError()
    if stage=='SCHEDULED':
     info=tk('POST','post/publish/creator_info/query/',json={});privacy={'PUBLIC':'PUBLIC_TO_EVERYONE','PRIVATE':'SELF_ONLY'}[d['visibility']]
     if privacy not in info.get('privacy_level_options',[]):raise ProtocolError()
     duration=d.get('asset_snapshot',{}).get('duration_seconds');maximum=info.get('max_video_post_duration_sec')
     if not isinstance(duration,(int,float)) or not isinstance(maximum,(int,float)) or not 0<duration<=maximum:raise ProtocolError()
     # Branded content is intentionally unsupported until its explicit disclosure
     # workflow is supplied; this adapter only accepts organic, non-brand posts.
     if d.get('disclosure')!='NONE':raise ProtocolError()
     ack=tk('POST','post/publish/video/init/',json={'post_info':{'title':d['caption'],'privacy_level':privacy,'disable_comment':True,'disable_duet':True,'disable_stitch':True,'brand_content_toggle':False,'brand_organic_toggle':False},'source_info':{'source':'PULL_FROM_URL','video_url':media_url}})
     return result('VERIFY',identifier(ack.get('publish_id')))
    identifier(remote);value=tk('POST','post/publish/status/fetch/',json={'publish_id':remote});state=value.get('status');ids=value.get('publicaly_available_post_id') # Provider's documented spelling.
    if state=='FAILED':return result('FAILED')
    if state=='PUBLISH_COMPLETE' and d['visibility']=='PUBLIC' and isinstance(ids,list) and ids and all(isinstance(v,str) and re.fullmatch('[0-9]{1,40}',v) for v in ids):return confirmed(remote,{'post_ids':ids})
    # PRIVATE completion has no public post proof. Expose pending remote review.
    return result('REMOTE_REVIEW' if state=='PUBLISH_COMPLETE' else 'VERIFY')
   raise ProtocolError()
 except (httpx.HTTPError,ProtocolError,ValueError,KeyError,TypeError,AttributeError):return result(fallback)
