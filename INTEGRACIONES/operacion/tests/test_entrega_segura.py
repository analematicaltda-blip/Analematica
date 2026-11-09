"""Actual disposable Git repos; never stage/commit/change the project repository."""
import importlib.util,json,os,shutil,subprocess,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('delivery',Path(__file__).resolve().parents[1]/'entrega_segura.py');tool=importlib.util.module_from_spec(spec);spec.loader.exec_module(tool)
class SafeDeliveryTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)/'source';self.root.mkdir();self.dest=Path(self.tmp.name)/'target';self.dest.mkdir();self.archive=Path(self.tmp.name)/'delivery.pyz'
  env={**os.environ,'GIT_CONFIG_GLOBAL':os.devnull,'GIT_CONFIG_NOSYSTEM':'1'}
  def git(*args):return subprocess.run(['git','-C',str(self.root),'-c','user.name=Disposable fixture','-c','user.email=fixture@example.test','-c','commit.gpgsign=false',*args],env=env,check=True,capture_output=True)
  self.git=git;git('init');(self.root/'existing.py').write_text('base\n');(self.root/'__pycache__').mkdir();(self.root/'__pycache__/cache.pyc').write_bytes(b'base generated cache');git('add','existing.py','__pycache__/cache.pyc');git('commit','-m','Disposable test base')
  (self.dest/'existing.py').write_text('base\n');(self.root/'existing.py').write_text('updated\n');(self.root/'nested').mkdir();(self.root/'nested/new.py').write_text('new\n')
 def package(self):tool.build(self.root,self.archive);return tool.load(self.archive)
 def test_full_modified_and_untracked_delivery_applies_and_replays(self):
  manifest,blobs=self.package();result=tool.apply(self.dest,manifest,blobs);self.addCleanup(shutil.rmtree,result['backup']);self.assertEqual(result['applied'],2);self.assertEqual((self.dest/'nested/new.py').read_text(),'new\n');self.assertEqual((self.dest/'existing.py').read_text(),'updated\n');self.assertEqual(tool.apply(self.dest,manifest,blobs)['applied'],0)
 def test_check_has_no_side_effects_and_preserves_source_git_head(self):
  head=self.git('rev-parse','HEAD').stdout;manifest,_=self.package();rows=tool.check(self.dest,manifest);self.assertEqual([r['state'] for r in rows],['READY','READY']);self.assertFalse((self.dest/'nested').exists());self.assertEqual(self.git('rev-parse','HEAD').stdout,head)
 def test_conflict_refuses_entire_delivery_before_any_change(self):
  manifest,blobs=self.package();(self.dest/'existing.py').write_text('a newer independent change\n')
  with self.assertRaises(ValueError):tool.apply(self.dest,manifest,blobs)
  self.assertFalse((self.dest/'nested').exists());self.assertEqual((self.dest/'existing.py').read_text(),'a newer independent change\n')
 def test_interrupted_application_rolls_back_and_keeps_recovery_journal(self):
  manifest,blobs=self.package();original=tool.write_atomic;backups=[]
  def write(path,data,mode):
   if path.name=='journal.json':backups.append(path.parent)
   if path==self.dest/'nested/new.py':raise OSError('Synthetic write failure')
   return original(path,data,mode)
  with patch.object(tool,'write_atomic',side_effect=write):
   with self.assertRaises(RuntimeError):tool.apply(self.dest,manifest,blobs)
  self.assertEqual((self.dest/'existing.py').read_text(),'base\n');self.assertFalse((self.dest/'nested/new.py').exists());self.assertEqual(json.loads((backups[-1]/'journal.json').read_text())['state'],'ROLLED_BACK');self.addCleanup(shutil.rmtree,backups[-1])
 def test_rollback_preserves_newer_concurrent_edit(self):
  manifest,blobs=self.package();original=tool.write_atomic;backups=[]
  def write(path,data,mode):
   if path.name=='journal.json':backups.append(path.parent)
   if path==self.dest/'nested/new.py':
    (self.dest/'existing.py').write_text('newer concurrent edit\n');raise OSError('Synthetic concurrent edit')
   return original(path,data,mode)
  with patch.object(tool,'write_atomic',side_effect=write):
   with self.assertRaises(RuntimeError):tool.apply(self.dest,manifest,blobs)
  self.assertEqual((self.dest/'existing.py').read_text(),'newer concurrent edit\n');journal=json.loads((backups[-1]/'journal.json').read_text());self.assertEqual(journal['state'],'RECOVERY_REQUIRED');self.assertEqual(journal['concurrent_changes'],['existing.py']);self.addCleanup(shutil.rmtree,backups[-1])
 def test_symlink_and_traversal_cannot_write_outside_destination(self):
  manifest,blobs=self.package();outside=Path(self.tmp.name)/'outside';outside.mkdir();(self.dest/'nested').symlink_to(outside,target_is_directory=True)
  with self.assertRaises(ValueError):tool.apply(self.dest,manifest,blobs)
  self.assertFalse((outside/'new.py').exists())
  for name in ['../escape','/absolute','.git/config','a/../escape','a\\escape','.env','a/private.key','.GIT/config','a/.ENV','bad./file','bad /file']:
   with self.assertRaises(ValueError):tool.relative(name)
 def test_tampered_payload_is_rejected_before_writing(self):
  self.package();changed=Path(self.tmp.name)/'tampered.pyz'
  with zipfile.ZipFile(self.archive) as source,zipfile.ZipFile(changed,'w') as target:
   for info in source.infolist():target.writestr(info.filename,b'tampered' if info.filename=='files/existing.py' else source.read(info.filename))
  with self.assertRaises(ValueError):tool.load(changed)
 def test_private_runtime_paths_and_private_key_material_are_not_packaged(self):
  (self.root/'.env').write_text('secret')
  with self.assertRaises(ValueError):tool.build(self.root,self.archive)
  (self.root/'.env').unlink();(self.root/'key.txt').write_text('-----BEGIN PRIVATE KEY-----\nprivate\n')
  with self.assertRaises(ValueError):tool.build(self.root,self.archive)
 def test_zipapp_is_directly_executable_for_dry_run(self):
  self.package();result=subprocess.run([__import__('sys').executable,str(self.archive),'check','--root',str(self.dest)],check=True,capture_output=True,text=True);self.assertEqual(json.loads(result.stdout)['ready'],2)
 def test_deletion_is_explicit_and_original_is_backed_up(self):
  (self.root/'existing.py').unlink();manifest,blobs=self.package();r=tool.apply(self.dest,manifest,blobs);self.addCleanup(shutil.rmtree,r['backup']);self.assertFalse((self.dest/'existing.py').exists());self.assertEqual((Path(r['backup'])/'files/existing.py').read_text(),'base\n')
 def test_generated_tracked_bytecode_is_explicitly_excluded(self):
  (self.root/'__pycache__/cache.pyc').write_bytes(b'changed generated cache');manifest,_=self.package();self.assertEqual(manifest['excluded_generated_files'],['__pycache__/cache.pyc']);self.assertEqual(len(manifest['entries']),2)
 def test_existing_archive_is_never_overwritten(self):
  self.package();before=self.archive.read_bytes()
  with self.assertRaises(ValueError):tool.build(self.root,self.archive)
  self.assertEqual(self.archive.read_bytes(),before)
if __name__=='__main__':unittest.main()
