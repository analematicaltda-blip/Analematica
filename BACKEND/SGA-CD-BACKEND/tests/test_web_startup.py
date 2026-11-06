"""Regression: an existing stopped web must start before nginx exec/reload."""
import importlib.util,subprocess,unittest
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('panel_web_startup',Path(__file__).resolve().parents[1]/'scripts/update_panels.py');updater=importlib.util.module_from_spec(spec);spec.loader.exec_module(updater)
class WebStartupTests(unittest.TestCase):
 compose=['docker','compose','-f','/private-demo/compose.json']
 def test_stopped_web_is_started_without_removing_data(self):
  state={'running':False};calls=[]
  def execute(argv,**kwargs):
   calls.append(argv);command=argv[len(self.compose):]
   if command[0]=='up':state['running']=True
   elif command[0]=='exec' and not state['running']:raise subprocess.CalledProcessError(1,argv)
   return subprocess.CompletedProcess(argv,0)
  with patch.object(updater,'run',side_effect=execute):updater.ensure_web_running(self.compose)
  self.assertEqual(calls[0],self.compose+['up','-d','--no-deps','--wait','--wait-timeout','90','web'])
  self.assertEqual(calls[1],self.compose+['exec','-T','web','nginx','-t']);self.assertEqual(calls[2],self.compose+['exec','-T','web','nginx','-s','reload'])
  self.assertFalse(any(value in ['down','rm','--volumes','--force-recreate'] for call in calls for value in call))
 def test_start_failure_stops_before_nginx_and_explains_diagnostics(self):
  with patch.object(updater,'run',side_effect=subprocess.CalledProcessError(1,['docker'])) as run:
   with self.assertRaisesRegex(SystemExit,'logs --tail 60 web'):updater.ensure_web_running(self.compose)
  self.assertEqual(run.call_count,1)
 def test_bad_nginx_config_is_not_reloaded(self):
  with patch.object(updater,'run',side_effect=[subprocess.CompletedProcess([],0),subprocess.CalledProcessError(1,['nginx'])]) as run:
   with self.assertRaises(subprocess.CalledProcessError):updater.ensure_web_running(self.compose)
  self.assertEqual(run.call_count,2)
if __name__=='__main__':unittest.main()
