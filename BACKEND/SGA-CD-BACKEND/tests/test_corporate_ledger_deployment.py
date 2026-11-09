"""Stage public assets in disposable compose, never starts or modifies a live node."""
import importlib.util,json,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('corporate_stage',ROOT/'BACKEND/ANALEMATICA-BACKEND/deployment/start.py');stage=importlib.util.module_from_spec(spec);spec.loader.exec_module(stage)
class CorporateLedgerDeployment(unittest.TestCase):
 def test_public_module_is_copied_and_existing_services_preserved(self):
  with tempfile.TemporaryDirectory(prefix='corporate-stage-test-') as private:
   demo=Path(private);before={'services':{'backend':{'image':'local-backend','environment':{'EXISTING':'kept'}},'web':{'image':'nginx:alpine','networks':['private']}}}
   (demo/'compose.json').write_text(json.dumps(before));release=stage.prepare(demo,8090,ROOT)
   script=release/'site/js/accounting-ledger.js'
   self.assertEqual(script.read_bytes(),(ROOT/'FRONTEND/ANALEMATICA-FRONTEND/js/accounting-ledger.js').read_bytes())
   self.assertIn('js/accounting-ledger.js',(release/'site/admin.html').read_text())
   self.assertEqual((release/'site/js/accounting-remediation.js').read_bytes(),(ROOT/'FRONTEND/ANALEMATICA-FRONTEND/js/accounting-remediation.js').read_bytes())
   self.assertIn('js/accounting-remediation.js',(release/'site/admin.html').read_text())
   after=json.loads((demo/'compose.json').read_text());self.assertEqual(after['services']['backend'],before['services']['backend']);self.assertEqual(after['services']['web'],before['services']['web'])
   self.assertEqual(after['services']['analematica']['networks'],['private']);self.assertEqual(json.loads((release/'compose.before.json').read_text()),before)
   for path in (release/'site').rglob('*'):
    if path.is_file():self.assertNotIn(path.suffix,{'.pem','.db','.sqlite','.env'})
if __name__=='__main__':unittest.main()
