import os
from .crm import CRMError
from .inbox_api import service
def run_once(limit=10):
 if os.environ.get('COMMERCIAL_INBOX_WORKER_ENABLED')!='1' or os.environ.get('COMMERCIAL_INBOX_NETWORK_ENABLED')!='1':raise CRMError('INBOX_WORKER_DISABLED',503)
 if type(limit)!=int or not 1<=limit<=50:raise CRMError('INBOX_WORKER_LIMIT')
 from .inbox_worker_context import candidates,context
 results=[];processed=0
 for ref,document in candidates():
  if processed>=limit:break
  try:
   with context(document) as crm:receipt=service(crm).dispatch(ref)
   processed+=1;results.append({'thread_id':ref,'status':receipt['status']})
  except Exception:results.append({'thread_id':ref,'status':'REVIEW_REQUIRED'})
 return results
def main():
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int,default=10);print(run_once(parser.parse_args().limit))
if __name__=='__main__':main()
