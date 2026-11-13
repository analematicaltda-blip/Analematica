"""Opt-in worker; re-resolves the original actor and own company for every step."""
import os
from .crm import CRMError
from .publishing_api import service
def run_once(limit=10):
 if os.environ.get('COMMERCIAL_PUBLISH_WORKER_ENABLED')!='1' or os.environ.get('COMMERCIAL_PUBLISH_NETWORK_ENABLED')!='1':raise CRMError('PUBLISH_WORKER_DISABLED',503)
 if type(limit)!=int or not 1<=limit<=50:raise CRMError('PUBLISH_WORKER_LIMIT')
 from .publishing_worker_context import candidates,context
 results=[]
 for ref,document in candidates()[:limit]:
  try:
   with context(document) as crm:receipt=service(crm).dispatch(ref)
   results.append({'job_id':ref,'status':receipt['status']})
  except Exception:results.append({'job_id':ref,'status':'REVIEW_REQUIRED'})
 return results
def main():
 import argparse,time
 parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int,default=10);parser.add_argument('--watch',action='store_true');args=parser.parse_args()
 while True:
  print(run_once(args.limit),flush=True)
  if not args.watch:break
  time.sleep(5)
if __name__=='__main__':main()
