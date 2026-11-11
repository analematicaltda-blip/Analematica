"""Compatibility export from the Analemática canonical contract."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
_name = "analematica_jarvi_contract"
if _name not in sys.modules:
    _source = Path(__file__).resolve().parents[4] / "ANALEMATICA-BACKEND" / "agents" / "contracts" / "jarvi_contract.py"
    _spec = spec_from_file_location(_name, _source)
    _module = module_from_spec(_spec)
    sys.modules[_name] = _module
    try:
        _spec.loader.exec_module(_module)
    except BaseException:
        sys.modules.pop(_name, None)
        raise
else:
    _module = sys.modules[_name]
globals().update({key: value for key, value in vars(_module).items() if not key.startswith("_")})
