"""SGA own DB isolation and active-role enforcement, independent of native ERP."""
import runpy,unittest,uuid
from pathlib import Path
from unittest.mock import patch
f=runpy.run_path(str(Path(__file__).with_name('test_pool08_crm.py')),run_name='landing_sga_setup')
from app.commercial.pool08.landing_models import CommercialLanding,LandingEvent
from app.models.user import Usuario
class Checks(unittest.TestCase):
 def setUp(self):
  f['CRMChecks'].setUp(self)
  for m in (CommercialLanding,LandingEvent):m.__table__.create(self.db.get_bind(),checkfirst=True)
 tearDown=f['CRMChecks'].tearDown;login=f['CRMChecks'].login
 def body(self):return dict(request_id=str(uuid.uuid4()),operation='create',landing_id=None,expected_revision=0,data={'slug':'pagina-'+uuid.uuid4().hex,'content':{'brand':'Propia','title':'Página','description':'Cultura','template':'CULTURA','blocks':[{'kind':'TEXT','heading':'Hola','body':'','url':'','label':''}]}})
 def post(self,b):return self.client.post('/api/v1/commercial-unified/crm/landing-commands',json=b)
 def get(self,path):return self.client.get('/api/v1/commercial-unified/crm/'+path)
 def test_foreign_company_cannot_edit_or_recover_receipt(self):
  b=self.body();r=self.post(b);self.assertEqual(r.status_code,200,r.text);ref=r.json()['landing_id'];self.login('other-admin_empresa');self.assertEqual(self.get('landings/'+ref).status_code,404);self.assertEqual(self.get('landing-receipts/'+b['request_id']).status_code,404)
 def test_role_revoked_cannot_replay_or_read(self):
  b=self.body();ref=self.post(b).json()['landing_id'];user=self.db.get(Usuario,self.users['full-admin_empresa']);user.rol='jefe_area';user.roles=[];self.db.commit();self.assertEqual(self.get('landings/'+ref).status_code,403);self.assertEqual(self.post(b).status_code,403)
 def test_transaction_rolls_back_failed_audit(self):
  from app.commercial.pool08.landing_store import Store
  with patch.object(Store,'append',side_effect=RuntimeError('synthetic audit unavailable')):
   with self.assertRaises(RuntimeError):self.post(self.body())
  self.assertEqual(self.db.query(CommercialLanding).count(),0)
 def test_index_tampering_is_not_accepted_as_valid_content(self):
  ref=self.post(self.body()).json()['landing_id'];self.db.query(CommercialLanding).filter_by(id=ref).update({'status':'PUBLISHED'});self.db.commit();self.assertEqual(self.get('landings/'+ref).status_code,503)
if __name__=='__main__':unittest.main()
