"""SGA CRM, live DB roles and canonical legacy records; no outbound services."""
import runpy,unittest,uuid
from pathlib import Path
from datetime import datetime,timedelta,timezone
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[3]
fixture=runpy.run_path(str(Path(__file__).resolve().parents[3] / 'BACKEND/tests/workspace/test_workspace.py'),run_name='sga_crm_fixture')
from app.commercial.pool08.api import router
from app.commercial.pool08.crm_models import CRMContact,CRMEvent
from app.models.workspace import WorkspaceLead,WorkspaceGrant
from app.models.user import Usuario
class CRMChecks(unittest.TestCase):
 def setUp(self):
  fixture['WorkspaceTests'].setUp(self);self.client.app.include_router(router,prefix='/api/v1/commercial-unified')
 tearDown=fixture['WorkspaceTests'].tearDown
 login=fixture['WorkspaceTests'].login
 def get(self,path='',**params):return self.client.get('/api/v1/commercial-unified/crm/'+path,params=params)
 def cmd(self,operation='create',contact=None,revision=0,**data):
  return dict(request_id=str(uuid.uuid4()),operation=operation,contact_id=contact,expected_revision=revision,data=data)
 def post(self,body):return self.client.post('/api/v1/commercial-unified/crm/commands',json=body)
 def create(self,**extra):
  data=dict(name='Persona CRM',email='cliente@example.test',phone='+573001234567',origin='MANUAL',responsible_ref=str(self.users['full-admin_empresa']));data.update(extra)
  r=self.post(self.cmd(**data));self.assertEqual(r.status_code,200,r.text);return r.json()['contact_id']
 def test_invalid_email_does_not_persist_contact_or_history(self):
  r=self.post(self.cmd(name='Invalid contact',email='bad'+chr(0)+'@example.test',phone='',origin='MANUAL',responsible_ref=str(self.users['full-admin_empresa'])))
  self.assertEqual(r.status_code,422,r.text);self.assertEqual(self.get('contacts').json()['contacts'],[]);self.assertEqual(self.db.query(CRMEvent).count(),0)
 def test_numeric_consent_hash_rejected_without_changing_revision(self):
  cid=self.create();r=self.post(self.cmd('consent',cid,1,channel='EMAIL',purpose='MARKETING',granted=False,evidence_digest=int('1'*64),expires_at=(datetime.now(timezone.utc)+timedelta(days=1)).isoformat()))
  self.assertEqual(r.status_code,422,r.text);self.assertEqual(self.get('contacts/'+cid).json()['revision'],1);self.assertEqual(len(self.get('contacts/'+cid+'/history').json()['events']),1)
 def test_escaped_invalid_unicode_is_422_not_server_failure(self):
  import json
  body=self.cmd(name='bad'+chr(0xD800),origin='MANUAL',responsible_ref=str(self.users['full-admin_empresa']))
  r=self.client.post('/api/v1/commercial-unified/crm/commands',content=json.dumps(body,ensure_ascii=True).encode(),headers={'Content-Type':'application/json'})
  self.assertEqual(r.status_code,422,r.text);self.assertEqual(self.get('contacts').json()['contacts'],[])
 def test_end_to_end_canonical_contact_and_reload(self):
  cid=self.create();self.assertIsNotNone(self.db.get(WorkspaceLead,cid))
  r=self.post(self.cmd('convert',cid,1));self.assertEqual(r.status_code,200,r.text)
  self.assertEqual(r.json()['customer_ref'],'workspace:'+cid)
  self.assertEqual(len(self.get('contacts').json()['contacts']),1)
  self.assertEqual(len(self.get('contacts/'+cid+'/history').json()['events']),2)
 def test_legacy_contact_adopted_with_identical_id(self):
  row=WorkspaceLead(id=str(uuid.uuid4()),scope='tenant:'+str(self.db.get(Usuario,self.users['full-admin_empresa']).inquilino_id),name='Previo',email='previo@example.test',notes='Notas anteriores',stage='contactado',created_by=self.users['full-admin_empresa']);self.db.add(row);self.db.commit()
  item=self.get('contacts/'+row.id).json();self.assertEqual(item['revision'],0)
  r=self.post(self.cmd('update',row.id,0,name='Revisado'));self.assertEqual(r.status_code,200,r.text)
  self.db.expire_all();self.assertEqual(self.db.get(WorkspaceLead,row.id).name,'Revisado');self.assertEqual(self.get('contacts/'+row.id).json()['notes'],'Notas anteriores')
 def test_foreign_company_no_access_or_idempotency_leak(self):
  cid=self.create();self.login('other-admin_empresa')
  self.assertEqual(self.get('contacts/'+cid).status_code,404);self.assertEqual(self.get('contacts').json()['contacts'],[])
 def test_live_revocation_and_wrong_responsible(self):
  self.assertEqual(self.post(self.cmd(name='X',origin='MANUAL',responsible_ref=str(self.users['other-admin_empresa']))).status_code,403)
  self.login('full-jefe_area');self.assertEqual(self.get('contacts').status_code,403)
  grant=self.db.query(WorkspaceGrant).filter_by(user_id=self.users['full-jefe_area'],permission='crm').one();grant.enabled=True;self.db.commit()
  self.assertEqual(self.get('contacts').status_code,200)
  grant.enabled=False;self.db.commit();self.assertEqual(self.get('contacts').status_code,403)
 def test_dedup_casefold_revision_and_replay(self):
  body=self.cmd(name='Uno',email='UPPER@example.test',origin='MANUAL',responsible_ref=str(self.users['full-admin_empresa']))
  r=self.post(body);self.assertEqual(r.status_code,200,r.text);cid=r.json()['contact_id']
  self.assertTrue(self.post(body).json()['replayed'])
  duplicate=self.post(self.cmd(name='Dos',email='upper@example.test',origin='MANUAL',responsible_ref=str(self.users['full-admin_empresa'])))
  self.assertEqual(duplicate.status_code,409);self.assertEqual(duplicate.json()['detail']['candidate_ids'],[cid])
  self.assertEqual(self.post(self.cmd('update',cid,0,name='Obsoleto')).status_code,409)
 def test_tasks_consent_withdrawal_and_channels(self):
  cid=self.create();due=(datetime.now(timezone.utc)+timedelta(days=1)).isoformat()
  r=self.post(self.cmd('task',cid,1,title='Llamar',due_at=due,responsible_ref=str(self.users['full-admin_empresa'])));self.assertEqual(r.status_code,200,r.text)
  consent=dict(channel='EMAIL',purpose='MARKETING',granted=True,evidence_digest='a'*64,expires_at=due)
  self.assertEqual(self.post(self.cmd('consent',cid,2,**consent)).status_code,200)
  self.assertEqual(self.post(self.cmd('withdraw',cid,3,reason='Baja solicitada')).status_code,200)
  self.assertFalse(self.get('contacts/'+cid).json()['consents']['EMAIL:MARKETING']['granted'])
  self.assertEqual(self.post(self.cmd('consent',cid,4,**consent)).status_code,409)
 def test_legacy_bypass_and_crm_suppression(self):
  from app.commercial.pool08.crm_delivery_guard import require_not_suppressed
  from fastapi import HTTPException
  cid=self.create()
  response=self.client.put('/api/v1/workspace/crm/leads/'+cid,json={'name':'Bypass','email':'otro@example.org','stage':'nuevo','notes':''})
  self.assertEqual(response.status_code,409)
  self.assertEqual(self.post(self.cmd('withdraw',cid,1,reason='Baja')).status_code,200)
  with self.assertRaises(HTTPException):require_not_suppressed(self.db,'tenant:'+str(self.db.get(Usuario,self.users['full-admin_empresa']).inquilino_id),'gmail','CLIENTE@example.test')
  require_not_suppressed(self.db,'foreign-company','gmail','cliente@example.test')
 def test_dedup_review_preserves_both_without_merging_consent(self):
  cid=self.create()
  second=self.create(name='Persona distinta',duplicate_review={'candidate_ids':[cid],'reason':'Personas distintas con teléfono compartido'})
  self.assertNotEqual(cid,second);self.assertEqual(self.get('contacts/'+second).json()['consents'],{})
 def test_email_change_revokes_channel_consent(self):
  cid=self.create();due=(datetime.now(timezone.utc)+timedelta(days=1)).isoformat()
  self.post(self.cmd('consent',cid,1,channel='EMAIL',purpose='MARKETING',granted=True,evidence_digest='a'*64,expires_at=due))
  self.assertEqual(self.post(self.cmd('update',cid,2,email='new@example.test')).status_code,200)
  self.assertFalse(self.get('contacts/'+cid).json()['consents']['EMAIL:MARKETING']['granted'])
 def test_error_paths_private_and_bounded(self):
  for r in [self.get('contacts',tenant='foreign'),self.get('contacts',offset=-1),self.client.post('/api/v1/commercial-unified/crm/commands',content=' '*17000,headers={'content-type':'application/json'})]:
   self.assertGreaterEqual(r.status_code,400);self.assertEqual(r.headers['cache-control'],'no-store')
 def test_failed_audit_rolls_back_contact(self):
  from sqlalchemy import event
  def fail(*args):raise RuntimeError('audit unavailable')
  event.listen(CRMEvent,'before_insert',fail)
  try:
   with self.assertRaises(RuntimeError):self.create()
  finally:event.remove(CRMEvent,'before_insert',fail)
  self.assertEqual(self.get('contacts').json()['contacts'],[])
if __name__=='__main__':unittest.main()
