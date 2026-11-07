import importlib.util
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('sqlite_snapshot',Path(__file__).resolve().parents[1]/'sqlite_snapshot.py')
snapshot=importlib.util.module_from_spec(spec)
spec.loader.exec_module(snapshot)


class SnapshotChecks(unittest.TestCase):
    def test_wal_backup_preserves_committed_records_and_source(self):
        with tempfile.TemporaryDirectory() as temp:
            source=Path(temp)/'source.sqlite3';target=Path(temp)/'backup.sqlite3'
            with sqlite3.connect(source) as live:
                live.execute('PRAGMA journal_mode=WAL')
                live.execute('CREATE TABLE evidence (id INTEGER PRIMARY KEY, body TEXT)')
                live.execute('INSERT INTO evidence VALUES (1,?)',('synthetic-test-only',));live.commit()
                before=snapshot.signature(live)
                report=snapshot.create_snapshot(source,target)
                self.assertTrue(report['restoration_verified'])
                self.assertEqual(snapshot.signature(live),before)
                with sqlite3.connect(target) as copied:self.assertEqual(snapshot.signature(copied),before)
                if os.name!='nt':self.assertEqual(target.stat().st_mode & 0o077,0)

    def test_existing_destination_and_source_alias_are_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            source=Path(temp)/'source.sqlite3';target=Path(temp)/'target.sqlite3'
            with sqlite3.connect(source) as live:live.execute('CREATE TABLE evidence (id INTEGER)')
            target.write_text('preserve')
            with self.assertRaises(FileExistsError):snapshot.create_snapshot(source,target)
            self.assertEqual(target.read_text(),'preserve')
            with self.assertRaises(FileExistsError):snapshot.create_snapshot(source,source)


if __name__=='__main__':unittest.main()
