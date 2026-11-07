"""Inspect installed migration sources without opening a database connection."""
import json
from django.apps import apps
from django.db.migrations.loader import MigrationLoader


def inspect_sources():
    loader = MigrationLoader(None, load=False)
    loader.load_disk()
    nodes = set(loader.disk_migrations)
    missing = []
    for key, migration in sorted(loader.disk_migrations.items()):
        for dependency in migration.dependencies:
            dependency = tuple(dependency)
            if dependency[1] in {'__first__', '__latest__'}:
                continue
            if dependency not in nodes:
                missing.append({'migration': list(key), 'missing_dependency': list(dependency)})
    unmigrated = []
    for config in apps.get_app_configs():
        models = [model._meta.label for model in config.get_models() if model._meta.managed and not model._meta.proxy]
        if models and not any(key[0]==config.label for key in nodes):
            unmigrated.append({'app':config.label, 'models':sorted(models)})
    return {'database_connected':False, 'migrations_applied':False, 'migration_count':len(nodes), 'missing_dependencies':missing, 'apps_without_migrations':unmigrated}


if __name__=='__main__':
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tourism_settings')
    django.setup()
    print(json.dumps(inspect_sources(), indent=2))
