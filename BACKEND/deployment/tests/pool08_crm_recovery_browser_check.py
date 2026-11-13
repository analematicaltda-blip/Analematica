"""Owned CRM delayed initialization and recovery DOM regressions with controlled transport."""
import os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
result=subprocess.run(['node',str(ROOT/'FRONTEND/deployment/tests/pool08_crm_recovery_browser.cjs')],cwd=ROOT,env={**os.environ,'NODE_PATH':'/tmp/sgacd-full-web-deps/node_modules'},timeout=100)
sys.exit(result.returncode)
