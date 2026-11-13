from pathlib import Path
import json
import os
import subprocess
import tempfile
import unittest

root=Path(__file__).resolve().parents[3]
class SetupTests(unittest.TestCase):
 def test_preserve_demo_and_credentials(self):
  with tempfile.TemporaryDirectory() as directory:
   demo=Path(directory);compose=demo/'compose.json'
   original={'services':{'postgres':{'image':'postgres:15-alpine'}},'volumes':{'database':{},'node6_state':{'external':True}}}
   compose.write_text(json.dumps(original))
   command=['python3',str(Path(__file__).resolve().parents[3] / 'BACKEND/tools/start_node6.py'),'--demo-dir',directory,'--prepare-only']
   env=os.environ.copy();env.pop('GEMINI_API_KEY',None)
   subprocess.run(command,check=True,capture_output=True,env=env)
   config=json.loads(compose.read_text());private=demo/'node6/node6.env'
   self.assertEqual(config['services']['postgres'],original['services']['postgres'])
   self.assertEqual(config['volumes'],original['volumes'])
   self.assertEqual(config['services']['node6']['ports'],['127.0.0.1:8606:8606'])
   self.assertEqual(private.stat().st_mode&0o777,0o600)
   credential=private.read_bytes();before=compose.read_bytes()
   subprocess.run(command,check=True,capture_output=True,env=env)
   self.assertEqual(private.read_bytes(),credential);self.assertEqual(compose.read_bytes(),before)
   bridge=(demo/'node6/matrix-mcp.json').read_text()
   token=dict(line.split('=',1) for line in credential.decode().splitlines() if '=' in line)['NODE6_TOKEN']
   self.assertNotIn(token,bridge)
   config['services']['node6']['ports']=['127.0.0.1:9999:8606'];compose.write_text(json.dumps(config));before=compose.read_bytes()
   self.assertNotEqual(subprocess.run(command,capture_output=True,env=env).returncode,0)
   self.assertEqual(compose.read_bytes(),before)
if __name__=='__main__':unittest.main()
