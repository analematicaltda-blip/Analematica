import runpy,unittest,sys,importlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'deployment/tests'))
from pool08_analytics_cases import AnalyticsCases
f=runpy.run_path(str(Path(__file__).with_name('test_pool08_generation.py')),run_name='analytics_sga_setup')
class Checks(AnalyticsCases,f['Checks']):
 def setUp(self):
  super().setUp();m=importlib.import_module(self.module_path+'.analytics_models')
  for model in (m.AnalyticsRecord,m.AnalyticsEvent):model.__table__.create(self.c.db.get_bind(),checkfirst=True)
if __name__=='__main__':raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(Checks(n) for n in unittest.defaultTestLoader.getTestCaseNames(AnalyticsCases))).wasSuccessful())
