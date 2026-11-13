"""Owned DOM recovery regressions with controlled transport; no backend acceptance."""
import os
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[3]
result=subprocess.run(['node',str(ROOT/'FRONTEND/deployment/tests/pool08_recovery_browser.cjs')],cwd=ROOT,env={**os.environ,'NODE_PATH':'/tmp/sgacd-full-web-deps/node_modules'},timeout=100)
sys.exit(result.returncode)
