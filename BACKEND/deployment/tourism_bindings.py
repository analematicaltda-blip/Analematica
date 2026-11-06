"""Bind relocated real Python packages to the namespaces used by Django."""
import importlib.util
import sys
import types
from pathlib import Path

def bind():
    root = Path(__file__).resolve().parents[1]
    import apps
    import apps.prestadores
    for name, directory in {
        'apps.core_erp': root / 'ANALEMATICA-BACKEND/core_erp',
        'apps.admin_plataforma': root / 'ANALEMATICA-BACKEND',
        'apps.prestadores.mi_negocio': root / 'SGA-ERP-TUR-BAKEND',
    }.items():
        if name in sys.modules:
            continue
        spec = importlib.util.spec_from_file_location(name, directory / '__init__.py', submodule_search_locations=[str(directory)])
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        parent_name, child = name.rsplit('.', 1)
        setattr(sys.modules[parent_name], child, module)
