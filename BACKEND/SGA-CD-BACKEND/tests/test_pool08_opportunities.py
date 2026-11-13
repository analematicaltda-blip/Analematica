"""SGA's opportunity flow, live permissions, exact values and audited rollback."""
import runpy,unittest,uuid,copy
from pathlib import Path
from datetime import datetime,timedelta,timezone
fixture=runpy.run_path(str(Path(__file__).with_name('test_pool08_crm.py')),run_name='opportunity_sga_fixture')
from app.commercial.pool08.opportunity_models import CommercialOpportunity,OpportunityEvent
from app.models.workspace import WorkspaceGrant
class OpportunityChecks(unittest.TestCase):
 setUp=fixture['CRMChecks'].setUp
 tearDown=fixture['CRMChecks'].tearDown
 login=fixture['CRMChecks'].login
 get=fixture['CRMChecks'].get
 post=fixture['CRMChecks'].post
 cmd=fixture['CRMChecks'].cmd
 create_contact=fixture['CRMChecks'].create
 def body(self,operation='create',ref=None,revision=0,**data):return dict(request_id=str(uuid.uuid4()),operation=operation,opportunity_id=ref,expected_revision=revision,data=data)
 def command(self,body):return self.client.post('/api/v1/commercial-unified/crm/opportunity-commands',json=body)
 def create(self,**extra):
  contact=self.create_contact();data=dict(title='Oferta turística',contact_id=contact,value='1250000.25',currency='COP',responsible_ref=str(self.users['full-admin_empresa']));data.update(extra)
  r=self.command(self.body(**data));self.assertEqual(r.status_code,200,r.text);return r.json()['opportunity_id']
 def transition(self,ref,revision,stage,**extra):return self.command(self.body('transition',ref,revision,stage=stage,reason='Avance documentado',**extra))
 def test_complete_pipeline_is_commercial_only(self):
  ref=self.create()
  for rev,stage in enumerate(('CONTACTED','QUALIFIED','PROPOSAL','NEGOTIATION','WON'),1):
   r=self.transition(ref,rev,stage,**({'confirmation':True,'evidence_digest':'a'*64} if stage=='WON' else {}));self.assertEqual(r.status_code,200,r.text)
   self.assertFalse(r.json()['payment_verified']);self.assertFalse(r.json()['ledger_written'])
  item=self.get('opportunities/'+ref).json();self.assertEqual(item['stage'],'WON');self.assertEqual(item['revision'],6);self.assertIsNone(item['score']['probability'])
  history=self.get('opportunities/'+ref+'/history').json();self.assertTrue(history['history_verified']);self.assertEqual(len(history['events']),5)
 def test_stage_jump_and_wrong_loss_are_rejected(self):
  ref=self.create();self.assertEqual(self.transition(ref,1,'WON').status_code,409);self.assertEqual(self.transition(ref,1,'LOST').status_code,422)
  self.assertEqual(self.transition(ref,1,'LOST',loss_code='TIMING',loss_detail='Nueva fecha pendiente').status_code,200)
  self.assertEqual(self.command(self.body('update',ref,2,title='Bypass')).status_code,409)
 def test_reopen_requires_local_administrator(self):
  ref=self.create();self.transition(ref,1,'LOST',loss_code='OTHER',loss_detail='Revisión')
  self.login('full-jefe_area');grant=self.db.query(WorkspaceGrant).filter_by(user_id=self.users['full-jefe_area'],permission='crm').one();grant.enabled=True;self.db.commit()
  self.assertEqual(self.command(self.body('reopen',ref,2,reason='Solicitud')).status_code,403)
  self.login('full-admin_empresa');self.assertEqual(self.command(self.body('reopen',ref,2,reason='Nueva gestión autorizada')).status_code,200)
 def test_cross_company_and_revoked_permissions(self):
  ref=self.create();self.login('other-admin_empresa');self.assertEqual(self.get('opportunities/'+ref).status_code,404);self.assertEqual(self.get('opportunities').json()['opportunities'],[])
  self.login('full-jefe_area');self.assertEqual(self.get('opportunities').status_code,403)
 def test_idempotency_revision_and_private_receipt(self):
  ref=self.create();body=self.body('update',ref,1,notes='Revisión')
  self.assertEqual(self.command(body).status_code,200);self.assertTrue(self.command(body).json()['replayed'])
  changed=copy.deepcopy(body);changed['data']['notes']='Otro';self.assertEqual(self.command(changed).status_code,409)
  self.assertEqual(self.command(self.body('update',ref,1,title='Antiguo')).status_code,409)
  self.assertEqual(self.get('opportunity-receipts/'+body['request_id']).json()['opportunity_id'],ref)
  self.login('other-admin_empresa');self.assertEqual(self.get('opportunity-receipts/'+body['request_id']).status_code,404)
 def test_rules_are_traceable_and_uncalibrated(self):
  ref=self.create(interest_evidence='b'*64,next_action={'description':'Validar propuesta','due_at':(datetime.now(timezone.utc)+timedelta(days=1)).isoformat(),'responsible_ref':str(self.users['full-admin_empresa'])})
  score=self.get('opportunities/'+ref).json()['score'];self.assertEqual(score['value'],100);self.assertFalse(score['dataset_evaluated']);self.assertTrue(all(r['source']['ref'] for r in score['criteria']))
 def test_unknown_money_and_financial_flags_are_rejected(self):
  contact=self.create_contact()
  for extra in ({'value':12.4},{'value':'1e2'},{'value':'1.001'},{'payment_verified':True},{'currency':'ANY'}):
   data=dict(title='Inválida',contact_id=contact,value='1.00',currency='COP',responsible_ref=str(self.users['full-admin_empresa']));data.update(extra)
   self.assertEqual(self.command(self.body(**data)).status_code,422)
 def test_follow_up_and_next_action(self):
  ref=self.create();r=self.command(self.body('task',ref,1,title='Llamar',due_at=(datetime.now(timezone.utc)+timedelta(days=1)).isoformat(),responsible_ref=str(self.users['full-admin_empresa'])));self.assertEqual(r.status_code,200,r.text)
  task=self.get('opportunities/'+ref).json()['tasks'][0];self.command(self.body('complete_task',ref,2,task_id=task['id']))
  self.assertTrue(self.get('opportunities/'+ref).json()['tasks'][0]['completed'])
 def test_withdrawn_contact_blocks_progress(self):
  ref=self.create();contact=self.get('opportunities/'+ref).json()['contact_id'];self.post(self.cmd('withdraw',contact,1,reason='Solicitud de baja'))
  self.assertEqual(self.transition(ref,1,'CONTACTED').status_code,409)
  self.assertEqual(self.get('opportunities/'+ref).json()['score']['value'],0)
 def test_audit_failure_rolls_back(self):
  from sqlalchemy import event
  def fail(*args):raise RuntimeError('audit unavailable')
  event.listen(OpportunityEvent,'before_insert',fail)
  try:
   with self.assertRaises(RuntimeError):self.create()
  finally:event.remove(OpportunityEvent,'before_insert',fail)
  self.assertEqual(self.db.query(CommercialOpportunity).count(),0)
 def test_tampered_history_and_state_fail_closed(self):
  ref=self.create();self.transition(ref,1,'CONTACTED');row=self.db.query(OpportunityEvent).filter_by(opportunity=ref).order_by(OpportunityEvent.sequence).first();doc=copy.deepcopy(row.document);doc['data']['title']='Alterada';row.document=doc;self.db.commit()
  r=self.get('opportunities/'+ref+'/history');self.assertEqual(r.status_code,503)
  r=self.transition(ref,2,'QUALIFIED');self.assertEqual(r.status_code,503)
  self.assertEqual(self.db.query(CommercialOpportunity).filter_by(id=ref).one().revision,2)
 def test_body_limits_and_private_errors(self):
  r=self.client.post('/api/v1/commercial-unified/crm/opportunity-commands',content=' '*17000,headers={'content-type':'application/json'});self.assertEqual(r.status_code,413);self.assertEqual(r.headers['cache-control'],'no-store')
if __name__=='__main__':unittest.main()
