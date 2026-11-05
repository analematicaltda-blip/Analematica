import importlib.util,json,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('corporate_deployment',Path(__file__).parents[1]/'deployment/start.py');node=importlib.util.module_from_spec(spec);spec.loader.exec_module(node)
class DeployTests(unittest.TestCase):
 def test_additive_node_only_public_assets_and_idempotent_service(self):
  repo=Path(__file__).resolve().parents[2]
  with tempfile.TemporaryDirectory() as name:
   demo=Path(name);original={'name':'existing','services':{'backend':{'image':'backend','volumes':['data:/data']},'web':{'image':'nginx:alpine'},'flet-mobile':{'image':'flet'}},'volumes':{'data':{}}};p=demo/'compose.json';p.write_text(json.dumps(original))
   for _ in range(2):release=node.prepare(demo,8090,repo)
   config=json.loads(p.read_text());self.assertEqual({k:v for k,v in config['services'].items() if k!='analematica'},original['services']);self.assertEqual(config['volumes'],original['volumes']);self.assertEqual(config['services']['analematica']['ports'],['127.0.0.1:8090:80']);self.assertEqual((release/'site').stat().st_mode&0o777,0o755);self.assertEqual((release/'site/js').stat().st_mode&0o777,0o755);self.assertFalse((release/'site/deployment').exists());self.assertFalse((release/'site/AGENTS_ARMY_ANALYSIS.md').exists());self.assertEqual(len(list((release/'site').rglob('*.html'))),3)
 def test_custom_service_not_overwritten(self):
  with tempfile.TemporaryDirectory() as name:
   demo=Path(name);p=demo/'compose.json';raw=json.dumps({'services':{'web':{},'backend':{},'analematica':{'image':'custom'}}});p.write_text(raw)
   with self.assertRaises(ValueError):node.prepare(demo,8090,Path(__file__).resolve().parents[2])
   self.assertEqual(p.read_text(),raw)
if __name__=='__main__':unittest.main()
