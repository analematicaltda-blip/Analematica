"""Compatibility launcher; active backend deployment lives in SGA-CD-BACKEND/scripts."""
from pathlib import Path
import importlib.util
spec=importlib.util.spec_from_file_location('sgacd_panel_installer',Path(__file__).resolve().parents[1]/'SGA-CD-BACKEND/scripts/update_panels.py')
_impl=importlib.util.module_from_spec(spec);spec.loader.exec_module(_impl)
install=_impl.install
subprocess=_impl.subprocess
BACKEND_FILES=_impl.BACKEND_FILES
if __name__=='__main__':_impl.main()
