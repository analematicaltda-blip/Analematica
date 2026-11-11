"""Offline deployment is deterministic, narrow and preserves unrelated files."""
import importlib.util,unittest,tempfile,json,re,hashlib
from pathlib import Path
source=Path(__file__).resolve().parents[1]/'accounting_offline_assets.py';spec=importlib.util.spec_from_file_location('capture_assets',source);engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
class AssetChecks(unittest.TestCase):
 def test_same_manifest_and_assets_for_both_web_origins(self):
  with tempfile.TemporaryDirectory() as tmp:
   a,b=Path(tmp)/'corporate',Path(tmp)/'erp';one=engine.install_assets(a);two=engine.install_assets(b);self.assertEqual(one,two);self.assertEqual(set(p.name for p in a.iterdir()),{'index.html','editor.js','editor.css','vault.js','worker.js'})
   for name,digest in one['assets'].items():self.assertEqual(hashlib.sha256((a/name).read_bytes()).hexdigest(),digest);self.assertEqual((a/name).read_bytes(),(b/name).read_bytes())
   self.assertFalse(one['api_cached']);self.assertEqual(one['scope'],'/contabilidad-offline/');self.assertEqual((a/'worker.js').read_bytes(),(b/'worker.js').read_bytes())
 def test_preparation_installs_capture_for_corporate_and_erp(self):
  spec=importlib.util.spec_from_file_location('capture_deployment',source.with_name('prepare.py'));deploy=importlib.util.module_from_spec(spec);spec.loader.exec_module(deploy)
  with tempfile.TemporaryDirectory() as tmp:
   deploy.RUNTIME=Path(tmp)/'runtime';dependencies=Path(tmp)/'deps';dependencies.mkdir();deploy.public_assets();deploy.nginx();deploy.next_projects(dependencies=str(dependencies),systems=('erp',))
   corporate=deploy.RUNTIME/'sites/analematica/contabilidad-offline';erp=deploy.RUNTIME/'erp/public/contabilidad-offline'
   self.assertTrue((deploy.RUNTIME/'sites/analematica/js/accounting-offline.js').is_file())
   config=(deploy.RUNTIME/'nginx.conf').read_text();self.assertEqual(config.count('location = /contabilidad-offline/worker.js { auth_basic off;'),2);self.assertEqual(config.count('location ^~ /contabilidad-offline/ { return 404; }'),2);self.assertEqual(config.count('auth_basic off; absolute_redirect off; return 302 /contabilidad-offline/index.html'),2);self.assertIn('auth_basic "Vista local erp"',config);self.assertNotIn('location /api/ { auth_basic off',config)
   for name in ['index.html','editor.js','editor.css','vault.js','worker.js']:self.assertEqual((corporate/name).read_bytes(),(erp/name).read_bytes());self.assertEqual((corporate/name).read_bytes(),(deploy.RUNTIME/'sites/erp-capture/contabilidad-offline'/name).read_bytes())
 def test_install_does_not_delete_unrelated_files(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);(p/'keep.txt').write_text('retain');engine.install_assets(p);self.assertEqual((p/'keep.txt').read_text(),'retain')
 def test_cannot_overwrite_symlink_or_symlink_destination(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);target=p/'target';target.write_text('private');d=p/'out';d.mkdir();(d/'vault.js').symlink_to(target)
   with self.assertRaises(ValueError):engine.install_assets(d)
   self.assertEqual(target.read_text(),'private');link=p/'link';link.symlink_to(d,target_is_directory=True)
   with self.assertRaises(ValueError):engine.install_assets(link)
if __name__=='__main__':unittest.main(verbosity=2)
