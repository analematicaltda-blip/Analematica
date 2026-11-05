#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


import pathlib

def main():
    """Run administrative tasks."""
    # Añadir el directorio 'backend' al sys.path
    # Esto permite que las apps en 'backend/apps' sean importables como 'apps.mi_app'
    BASE_DIR = pathlib.Path(__file__).resolve().parent
    sys.path.insert(0, str(BASE_DIR))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "puerto_gaitan_turismo.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
