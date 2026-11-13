"""Compatibility runner; wallet tests are maintained in BACKEND/WALLET-BACKEND/tests."""
from pathlib import Path
import runpy
globals().update(runpy.run_path(str(Path(__file__).resolve().parents[3]/"BACKEND/WALLET-BACKEND/tests"/'device_approval_check.py'),run_name=__name__))
