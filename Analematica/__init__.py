"""Compatibility namespace for Python imports after moving the backend."""
import importlib.util
import sys
from pathlib import Path

_path = Path(__file__).resolve().parents[1] / 'BACKEND' / 'ANALEMATICA-BACKEND'
_spec = importlib.util.spec_from_file_location(__name__ + '.backend', _path / '__init__.py', submodule_search_locations=[str(_path)])
backend = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = backend
_spec.loader.exec_module(backend)
