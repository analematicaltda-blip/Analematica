"""Readiness contracts using real Django setup and controlled schema probes."""
import os
import runpy
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

runpy.run_path(str(Path(__file__).with_name('tourism_runtime_check.py')), run_name='fixture_setup')
from schema_readiness import inspect_schema
from django.db.migrations.exceptions import NodeNotFoundError
from django.db.utils import OperationalError
from rest_framework.test import APIClient


class ReadinessChecks(unittest.TestCase):
    def test_real_legacy_graph_blocks_readiness_without_leaking_details(self):
        response = APIClient(HTTP_HOST='localhost').get('/readyz')
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()['checks'], ['migration_history_invalid'])
        self.assertNotIn('prestadores', response.content.decode())
        self.assertEqual(response['Cache-Control'], 'no-store')

    def probe(self, pending=False, tables=('sample',), columns=('id',)):
        executor = MagicMock()
        executor.migration_plan.return_value = [object()] if pending else []
        meta = SimpleNamespace(db_table='sample', can_migrate=lambda conn: True, local_fields=[SimpleNamespace(column='id')])
        with patch('schema_readiness.MigrationExecutor', return_value=executor), patch('schema_readiness.apps.get_models', return_value=[SimpleNamespace(_meta=meta)]), patch('schema_readiness.connection.introspection.table_names', return_value=tables), patch('schema_readiness.connection.introspection.get_table_description', return_value=[SimpleNamespace(name=name) for name in columns]):
            return inspect_schema()

    def test_pending_migrations_are_not_ready(self):
        self.assertEqual(self.probe(pending=True)['checks'], ['pending_migrations'])

    def test_unmigrated_app_table_is_required(self):
        self.assertEqual(self.probe(tables=())['checks'], ['missing_tables'])

    def test_model_columns_are_required(self):
        self.assertEqual(self.probe(columns=())['checks'], ['missing_columns'])

    def test_valid_schema_contract_is_ready(self):
        self.assertEqual(self.probe(), {'status':'ready', 'checks':[]})

    def test_database_failure_is_sanitized(self):
        with patch('schema_readiness.MigrationExecutor', side_effect=OperationalError('private database credentials')):
            self.assertEqual(inspect_schema(), {'status':'not_ready', 'checks':['database_unavailable']})

    def test_readiness_has_no_migration_execution(self):
        with patch('django.core.management.call_command', side_effect=AssertionError('must not run management commands')):
            self.assertEqual(APIClient(HTTP_HOST='localhost').get('/readyz').status_code,503)

    def test_source_audit_reports_all_missing_dependencies_without_sql(self):
        from migration_preflight import inspect_sources
        from django.db import connection
        def refuse(*args, **kwargs):
            raise AssertionError('Source audit must not query the database')
        with connection.execute_wrapper(refuse):
            report=inspect_sources()
        self.assertFalse(report['database_connected'])
        self.assertTrue(any(item['missing_dependency']==['prestadores','0001_full_reset'] for item in report['missing_dependencies']))
        self.assertTrue(any(item['app']=='prestadores' for item in report['apps_without_migrations']))


if __name__=='__main__': unittest.main()
