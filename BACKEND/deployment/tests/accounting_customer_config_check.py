"""Customer configuration path and strict JSON boundaries, no external accounts."""
import sys,tempfile,unittest,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'BACKEND/ANALEMATICA-BACKEND'))
from core_erp.accounting.customer_package_api import private_json
class CustomerConfigChecks(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.path=self.root/'grant.json'
 def save(self,raw):self.path.write_text(raw);self.path.chmod(0o600)
 def test_private_regular_file_accepted(self):self.save('{"version":1}');self.assertEqual(private_json(self.path),{'version':1})
 def test_duplicate_keys_and_nonfinite_rejected(self):
  for raw in ['{"permissions":["read"],"permissions":["append"]}','{"x":NaN}','{"x":Infinity}']:
   self.save(raw)
   with self.assertRaises(ValueError):private_json(self.path)
 def test_symlink_file_and_parent_rejected(self):
  self.save('{}');link=self.root/'link.json';link.symlink_to(self.path)
  with self.assertRaises(ValueError):private_json(link)
  directory=self.root/'parent-link';directory.symlink_to(self.root,target_is_directory=True)
  with self.assertRaises(ValueError):private_json(directory/'grant.json')
 def test_public_permissions_rejected(self):
  self.save('{}');self.path.chmod(0o644)
  with self.assertRaises(ValueError):private_json(self.path)
 def test_nonregular_fifo_rejected_without_blocking(self):
  os.mkfifo(self.path,0o600)
  with self.assertRaises(ValueError):private_json(self.path)
 def test_oversize_rejected(self):
  self.save(' '*16385)
  with self.assertRaises(ValueError):private_json(self.path)
 def test_relative_path_rejected(self):
  with self.assertRaises(ValueError):private_json('grant.json')
if __name__=='__main__':unittest.main(verbosity=2)
