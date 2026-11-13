"""Opt-in local SMTP adapter. Acceptance by SMTP never proves delivery or opening."""
import smtplib,os
from .crm import digest
from email.message import EmailMessage
from .email_campaigns import EmailCampaigns
from .email_campaign_store import Store
def process(crm,ref,contact,smtp_factory=None):
 engine=EmailCampaigns(Store(crm.store),crm);claim=engine.claim(ref,contact)
 if claim is None:return None
 d,r,token,rendered=claim;p=engine.policy();message=EmailMessage();message['From']=p['sender_email'];message['To']=r['email'];message['Subject']=rendered['subject'];message['Message-ID']=r['message_id'];message['List-Unsubscribe']='<'+rendered['unsubscribe_url']+'>';message['List-Unsubscribe-Post']='List-Unsubscribe=One-Click';message.set_content(rendered['text']);message.add_alternative(rendered['html'],subtype='html')
 try:
  with engine.store.transaction():
   engine.store.lock();engine.authority()
   current=engine.policy()
   if os.environ.get('COMMERCIAL_EMAIL_WORKER_ENABLED')!='1' or not current['allow_dispatch'] or digest(current)!=d['sender_policy_digest'] or engine.suppressed(r['email']) or not engine.eligible(contact,r['email']) or digest(engine.crm.get(contact).get('consents',{}).get('EMAIL:MARKETING',{}))!=r['consent_digest']:return engine.finish(ref,contact,token,'SUPPRESSED')
   with (smtp_factory or smtplib.SMTP)(p['smtp_host'],p['smtp_port'],timeout=10) as smtp:refused=smtp.send_message(message)
  status='REJECTED' if refused else 'ACCEPTED'
 except smtplib.SMTPRecipientsRefused:status='REJECTED'
 except (OSError,smtplib.SMTPException):status='UNCERTAIN'
 return engine.finish(ref,contact,token,status)

def run_once(limit=10):
 import os
 from .crm import CRMError
 if os.environ.get('COMMERCIAL_EMAIL_WORKER_ENABLED')!='1':raise CRMError('EMAIL_WORKER_DISABLED',503)
 if type(limit)!=int or not 1<=limit<=100:raise CRMError('EMAIL_WORKER_LIMIT')
 from .email_campaign_worker_context import candidates,context
 results=[]
 for ref,document in candidates():
  for recipient in document.get('recipients',[]):
   if len(results)>=limit:return results
   if recipient['status']!='PENDING':continue
   try:
    with context(document) as crm:result=process(crm,ref,recipient['contact_id'])
    results.append({'campaign_id':ref,'status':result['status'] if result else 'SKIPPED'})
   except Exception:results.append({'campaign_id':ref,'status':'BLOCKED_REQUIRES_REVIEW'})
 return results
def main():
 import argparse,time
 p=argparse.ArgumentParser();p.add_argument('--limit',type=int,default=10);p.add_argument('--watch',action='store_true');args=p.parse_args()
 while True:
  print(run_once(args.limit),flush=True)
  if not args.watch:break
  time.sleep(5)
if __name__=='__main__':main()
