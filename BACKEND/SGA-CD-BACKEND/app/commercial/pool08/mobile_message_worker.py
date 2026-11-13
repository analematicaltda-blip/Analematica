"""Own opt-in outbound worker. A durable claim precedes network dispatch."""
import os
from .crm import CRMError,digest
from .mobile_messages import MobileMessages
from .mobile_message_store import Store
from .mobile_message_adapters import dispatch,credential
def process(crm,ref,client_factory=None):
 engine=MobileMessages(Store(crm.store),crm)
 if os.environ.get('COMMERCIAL_MOBILE_NETWORK_ENABLED')!='1':raise CRMError('MOBILE_NETWORK_DISABLED',503)
 pre=engine.get(ref);credential(engine.policy(pre['channel']))
 claim=engine.claim(ref)
 if claim is None:return None
 d,p,token,prepared=claim
 with engine.store.transaction():
  engine.store.lock();engine.authority(d['channel']);current=engine.policy(d['channel'])
  if not current['allow_dispatch'] or digest(current)!=d['policy_digest'] or not engine.eligible(d):return engine.finish(ref,token,'SUPPRESSED')
  if engine.prepare(d,current)!=prepared:raise CRMError('MOBILE_MEDIA_OR_QUOTE_CHANGED',409)
  result=dispatch(d,current,prepared,client_factory=client_factory)
 return engine.finish(ref,token,result['status'],result['provider_id'])
def run_once(limit=10):
 if os.environ.get('COMMERCIAL_MOBILE_WORKER_ENABLED')!='1' or os.environ.get('COMMERCIAL_MOBILE_NETWORK_ENABLED')!='1':raise CRMError('MOBILE_WORKER_OR_NETWORK_DISABLED',503)
 if type(limit)!=int or not 1<=limit<=100:raise CRMError('MOBILE_WORKER_LIMIT')
 from .mobile_message_worker_context import candidates,context
 results=[]
 for ref,document in candidates():
  if len(results)>=limit:break
  try:
   with context(document) as crm:result=process(crm,ref)
   results.append({'job_id':ref,'status':result['status'] if result else 'SKIPPED'})
  except Exception:results.append({'job_id':ref,'status':'BLOCKED_REQUIRES_REVIEW'})
 return results
def main():
 import argparse,time
 p=argparse.ArgumentParser();p.add_argument('--watch',action='store_true');p.add_argument('--limit',type=int,default=10);args=p.parse_args()
 while True:
  print(run_once(args.limit),flush=True)
  if not args.watch:break
  time.sleep(5)
if __name__=='__main__':main()
