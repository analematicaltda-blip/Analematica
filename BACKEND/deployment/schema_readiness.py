"""Read-only schema readiness. Never migrate, fake history, or expose SQL errors."""
from django.apps import apps
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.exceptions import InvalidBasesError, NodeNotFoundError, CircularDependencyError, InconsistentMigrationHistory
from django.db.utils import DatabaseError


def inspect_schema():
    issues = []
    try:
        executor = MigrationExecutor(connection)
        executor.loader.check_consistent_history(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        if plan:
            issues.append('pending_migrations')
        # Include apps without migrations: a valid graph alone does not prove tables exist.
        with connection.cursor() as cursor:
            tables = set(connection.introspection.table_names(cursor))
            for model in apps.get_models(include_auto_created=True):
                if not model._meta.can_migrate(connection):
                    continue
                table = model._meta.db_table
                if table not in tables:
                    issues.append('missing_tables')
                    continue
                columns = {column.name for column in connection.introspection.get_table_description(cursor, table)}
                if any(field.column not in columns for field in model._meta.local_fields):
                    issues.append('missing_columns')
        if {'core_erp_journalentry','core_erp_ledgerentry','core_erp_accountingratiopolicy'}<=tables:
            from apps.core_erp.accounting.sql_guard_health import inspect_guards
            issues.extend(inspect_guards(connection)['checks'])
            from django.conf import settings
            if getattr(settings,'ACCOUNTING_ENFORCE_DB_PRIVILEGES',False):
                from apps.core_erp.accounting.db_privileges import inspect_privileges
                issues.extend(inspect_privileges(connection)['checks'])
    except (NodeNotFoundError, CircularDependencyError, InvalidBasesError, InconsistentMigrationHistory):
        issues.append('migration_history_invalid')
    except DatabaseError:
        issues.append('database_unavailable')
    return {'status': 'ready' if not issues else 'not_ready', 'checks': sorted(set(issues))}
