"""Disposable planning profiles only: no credentials, provider calls or spending."""
import json,os
def configure(system,scope,provider=None):
 key=system+':'+str(scope)+':'+(str(provider) if provider else '-')
 os.environ['COMMERCIAL_ADS_LIMITS']=json.dumps({system+':'+str(scope):{'version':'fixture-1','currency':'COP','max_reserved_minor':1000000,'max_daily_minor':500000,'support_digest':'a'*64}})
 os.environ['COMMERCIAL_ADS_ACCOUNTS']=json.dumps({key:{platform:{'version':'fixture-1','platform':platform,'account_id':'declared-fixture','currency':'COP','ownership_support_digest':'b'*64} for platform in ['META','TIKTOK','GOOGLE_YOUTUBE']}})
