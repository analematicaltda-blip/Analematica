"""Synthetic connector profiles only: no secrets/accounts from real providers."""
import os,json
KEY='synthetic-inbox-ingress-00000000000000'
CHANNELS=['FB_DM','IG_DM','FB_COMMENT','IG_COMMENT','EMAIL','WHATSAPP','YOUTUBE_COMMENT','TIKTOK_DM','TIKTOK_COMMENT']
def configure(system,scope,provider=None):
 key=system+':'+str(scope)+':'+(str(provider) if provider else '-')
 profiles={channel:{'version':'fixture-1','channel':channel,'account_id':'owner@example.test' if channel=='EMAIL' else 'UC'+'x'*22 if channel=='YOUTUBE_COMMENT' else '123','page_id':'456','credential_env':'COMMERCIAL_INBOX_SECRET_FIXTURE','ingress_key_env':'COMMERCIAL_INBOX_INGRESS_FIXTURE','allow_reply':False,'ownership_support_digest':'a'*64} for channel in CHANNELS}
 os.environ['COMMERCIAL_INBOX_ACCOUNTS']=json.dumps({key:profiles});os.environ['COMMERCIAL_INBOX_INGRESS_FIXTURE']=KEY;os.environ['COMMERCIAL_INBOX_WORKER_ENABLED']='0';os.environ['COMMERCIAL_INBOX_NETWORK_ENABLED']='0'
