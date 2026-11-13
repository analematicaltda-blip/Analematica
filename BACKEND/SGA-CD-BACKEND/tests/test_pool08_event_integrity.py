"""SQLAlchemy event routing/index integrity for the eight own commercial domains."""
import importlib,runpy,unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'deployment/tests'))
from pool08_event_cases import EventBindingCases,DOMAINS
fixture=runpy.run_path(str(Path(__file__).with_name('test_pool08_state_integrity.py')),run_name='event_sga_setup')
for domain,name in DOMAINS:importlib.import_module('app.commercial.pool08.'+domain+'_models')

def cases(domain,modelname):
 model=getattr(importlib.import_module('app.commercial.pool08.'+domain+'_models'),modelname)
 class Checks(EventBindingCases,unittest.TestCase):
  def setUp(self):
   self.c=fixture['StateIntegrityChecks']();self.c.setUp();self.addCleanup(self.c.doCleanups);self.base=self.c.base;self.db=self.c.db
   self.store=importlib.import_module('app.commercial.pool08.'+domain+'_store').Store(self.base)
   self.error=fixture['CRMError'];self.digest=fixture['digest'];self.domain=domain;self.item_field='opportunity' if domain=='opportunity' else 'item_id'
  def insert(self,rid,item,doc):self.db.add(model(id=rid,scope=self.base.scope,**{self.item_field:item},document=doc));self.db.commit()
  def update(self,rid,**values):self.db.query(model).filter_by(id=rid).update(values,synchronize_session=False);self.db.commit();self.db.expire_all()
 return Checks
for domain,model in DOMAINS:globals()['SGA_'+domain]=cases(domain,model)
if __name__=='__main__':unittest.main()
