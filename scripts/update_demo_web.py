"""Compatibility launcher; web publishing lives in the frontend module."""
from pathlib import Path
import runpy
if __name__=='__main__':runpy.run_path(str(Path(__file__).resolve().parents[1]/'SGA-CD-WEB.git/scripts/publish.py'),run_name='__main__')
