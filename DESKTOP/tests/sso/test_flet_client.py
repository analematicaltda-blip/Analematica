import asyncio
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch, Mock, AsyncMock

root=Path(__file__).resolve().parents[3]
class Session:
 def __init__(self):self.values={}
 def get(self,key):return self.values.get(key)
 def set(self,key,value):self.values[key]=value
 def remove(self,key):self.values.pop(key,None)
class FletClientTests(unittest.TestCase):
 def test_each_client_receives_central_session_without_local_database(self):
  for folder in ['DESKTOP/SGA-CD-APP.git','MOVILES/SGA-CD-APK.git']:
   spec=importlib.util.spec_from_file_location('client',root/folder/'utils/sso_client.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
   page=SimpleNamespace(session=Session(),go=Mock(),launch_url=Mock(),update=Mock())
   tasks=[];page.run_task=tasks.append;message=SimpleNamespace(value='')
   user=dict(id=900,email='member@gmail.com',nombre='Member',roles=['profesor'],inquilino_id=7)
   reply=dict(status='authenticated',access_token='test-access',refresh_token='test-refresh',user=user)
   responses=[Mock(ok=True,json=lambda:dict(flow_id='test',proof='proof',authorization_url='https://sga.example/authorize',expires_in=30)),Mock(ok=True,json=lambda:reply)]
   with patch.dict(module.os.environ,{'SGACD_API_BASE_URL':'https://sga.example'}),patch.object(module.requests,'post',side_effect=responses),patch.object(module.asyncio,'sleep',new=AsyncMock()):
    module.begin_sso(page,'google',message,'test-only-password');asyncio.run(tasks[0]())
   page.go.assert_called_once_with('/sso/account')
   self.assertEqual(page.session.get('sso_session')['user']['roles'],['profesor'])
   self.assertFalse(page.session.get('sso_pending'))
   view=module.account_view(page)
   self.assertEqual(view.route,'/sso/account')
if __name__=='__main__':unittest.main()
