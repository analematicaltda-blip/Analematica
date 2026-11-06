"""Compatibility entry point; deployment is owned by BACKEND/ANALEMATICA-BACKEND."""
import importlib.util
from pathlib import Path
source=Path(__file__).resolve().parents[3]/'BACKEND/ANALEMATICA-BACKEND/deployment/start.py'
spec=importlib.util.spec_from_file_location('analematica_deployment',source)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
prepare=module.prepare
PUBLIC=module.PUBLIC
if __name__=='__main__':module.main()
