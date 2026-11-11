"""Compatibility entry point; canonical legacy staff is owned by Analemática."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

_name = "analematica_legacy_command_staff"
if _name not in sys.modules:
    _source = Path(__file__).resolve().parents[3] / "ANALEMATICA-BACKEND" / "agents" / "legacy_command_staff.py"
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
JarviGeneralOrchestrator = _module.JarviGeneralOrchestrator
NekoConversationalGeneral = _module.NekoConversationalGeneral
