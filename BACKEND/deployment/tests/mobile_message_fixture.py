"""Only disposable test servers import this configuration. No real provider credentials."""
import os,json
def configure(system,scope,provider=None):
 key=system+':'+str(scope)+':'+(str(provider) if provider else '-')
 base={'version':'fixture-1','adapter':'twilio-sms','from_id':'+15550000001','credential_env':'COMMERCIAL_MOBILE_SECRET_UNUSED_FIXTURE','limit_daily':10,'max_segments':3,'estimate_minor':100,'currency':'COP','co_support_digest':'a'*64,'allow_dispatch':False,'media_max_bytes':1048576,'public_base_url':'https://media.example.test','wa_template_name':'','wa_language':'','wa_template_digest':'','allow_sms_link':True,'allowed_media_kinds':['IMAGE','VIDEO'],'wa_header_kind':'','media_max_seconds':60,'wa_template_body':''}
 policies={'SMS':base,'MMS':{**base,'adapter':'twilio-mms'},'WHATSAPP':{**base,'adapter':'meta-whatsapp','from_id':'12345678','wa_template_name':'fixture_template','wa_language':'es_CO','wa_template_digest':'b'*64,'wa_header_kind':'IMAGE','wa_template_body':'Información autorizada: {{body}}'}}
 os.environ['COMMERCIAL_MOBILE_POLICIES']=json.dumps({key:policies});os.environ['COMMERCIAL_MOBILE_RECEIPT_KEYS']=json.dumps({key:'synthetic-mobile-fixture-key-only-32'});os.environ['COMMERCIAL_MOBILE_WORKER_ENABLED']='0';os.environ['COMMERCIAL_MOBILE_NETWORK_ENABLED']='0'
