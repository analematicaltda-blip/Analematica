"""Disposable HTTP configuration only. No provider token and no worker execution."""
import os,json
def configure(system,scope,provider=None):
 key=system+':'+str(scope)+':'+(str(provider) if provider else '-')
 profile={'version':'fixture-1','format':'FACEBOOK_PHOTO','account_id':'123','page_id':'','credential_env':'COMMERCIAL_PUBLISH_SECRET_FIXTURE','public_base_url':'https://media.example.test','allow_publish':False,'ownership_support_digest':'a'*64,'daily_limit':10}
 os.environ['COMMERCIAL_PUBLISH_ACCOUNTS']=json.dumps({key:{'owned-page-fixture':profile}});os.environ['COMMERCIAL_PUBLISH_WORKER_ENABLED']='0';os.environ['COMMERCIAL_PUBLISH_NETWORK_ENABLED']='0'
