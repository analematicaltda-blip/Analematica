"""Validate adapter payloads against Open Duet's actual vendored public schemas."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from app.services.assistance.duet import agent_payload

class OpenDuetContractTests(unittest.TestCase):
    def test_actual_upstream_schemas_accept_the_plan_only_payloads(self):
        root=Path(__file__).resolve().parents[3]
        environment={**os.environ,'PYTHONPATH':str(root/'DESKTOP/open-duet/backend')}
        script='''import json,sys
from app.schemas.agent import AgentCreateRequest
from app.schemas.thread import ThreadCreateRequest,TurnCreateRequest
payload=json.load(sys.stdin)
agent=AgentCreateRequest.model_validate(payload)
assert agent.approval_mode=='plan' and not agent.make_lead and not agent.memory_enabled
ThreadCreateRequest.model_validate({'provider':'codex','agent_id':1,'title':'Asistencia local'})
TurnCreateRequest.model_validate({'prompt_text':'Orienta sin ejecutar acciones.'})
print('Actual upstream schema contract passed.')
'''
        result=subprocess.run([sys.executable,'-c',script],input=json.dumps(agent_payload('contract-test')),env=environment,text=True,capture_output=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('contract passed',result.stdout)

if __name__=='__main__':unittest.main()
