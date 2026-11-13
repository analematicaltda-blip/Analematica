"""Owned composition UI with a real MP4 produced by the preceding ORM suite."""
import os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.exit(subprocess.run(['node',str(ROOT/'FRONTEND/deployment/tests/pool08_video_browser.cjs')],cwd=ROOT,env={**os.environ,'NODE_PATH':'/tmp/sgacd-full-web-deps/node_modules'},timeout=100).returncode)
