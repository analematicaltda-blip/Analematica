"""Compatibility import; renderer implementation belongs to the frontend module."""
from pathlib import Path
import importlib.util
spec=importlib.util.spec_from_file_location('sgacd_landing_renderer',Path(__file__).resolve().parents[1]/'FRONTEND/SGA-CD-WEB.git/scripts/render_landing.py')
_impl=importlib.util.module_from_spec(spec);spec.loader.exec_module(_impl)
render=_impl.render
