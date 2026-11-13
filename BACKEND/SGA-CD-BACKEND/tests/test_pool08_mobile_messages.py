import runpy,unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'deployment/tests'))
from pool08_mobile_message_cases import MobileCases
f=runpy.run_path(str(Path(__file__).with_name('test_pool08_generation.py')),run_name='campaign_sga_setup')
class Checks(MobileCases,f['Checks']):pass
if __name__=='__main__':raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(Checks(n) for n in unittest.defaultTestLoader.getTestCaseNames(MobileCases))).wasSuccessful())
