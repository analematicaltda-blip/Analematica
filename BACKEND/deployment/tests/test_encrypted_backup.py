"""Authenticated backup failure cases using isolated SQLite, never project data."""
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('encrypted_backup',Path(__file__).resolve().parents[1]/'encrypted_backup.py')
backup=importlib.util.module_from_spec(spec);spec.loader.exec_module(backup)

class EncryptedBackupTests(unittest.TestCase):
    def setUp(self):
        self.private=tempfile.TemporaryDirectory();self.root=Path(self.private.name)
        self.source=self.root/'source.sqlite3';self.key=self.root/'backup.key'
        self.archive=self.root/'database.sgacdb';self.destination=self.root/'restored.sqlite3'
        backup.keygen(self.key)
        with sqlite3.connect(self.source) as db:
            db.execute('CREATE TABLE documents(id INTEGER PRIMARY KEY, payload TEXT)')
            db.execute('INSERT INTO documents(payload) VALUES (?)',('private-fixture-content',))
    def tearDown(self):self.private.cleanup()
    def seal(self):return backup.backup(self.source,self.archive,self.key,'erp-tur')
    def test_round_trip_plaintext_never_appears_in_archive(self):
        self.seal();self.assertNotIn(b'private-fixture-content',self.archive.read_bytes())
        self.assertTrue(backup.verify(self.archive,self.key,'erp-tur')['verified'])
        result=backup.restore(self.archive,self.destination,self.key,'erp-tur')
        self.assertTrue(result['restored_to_new_database'])
        self.assertFalse(result['application_keys_included'])
        with sqlite3.connect(self.destination) as db:
            self.assertEqual(db.execute('SELECT payload FROM documents').fetchone()[0],'private-fixture-content')
        for p in [self.key,self.archive,self.destination]:self.assertEqual(p.stat().st_mode&0o777,0o600)
    def test_source_database_and_key_not_changed(self):
        before=self.source.read_bytes();key=self.key.read_bytes();self.seal()
        self.assertEqual(self.source.read_bytes(),before);self.assertEqual(self.key.read_bytes(),key)
        with self.assertRaises(backup.BackupError):backup.keygen(self.key)
        self.assertEqual(self.key.read_bytes(),key)
    def test_tampered_ciphertext_rejected_before_destination_creation(self):
        self.seal();data=bytearray(self.archive.read_bytes());data[-1]^=1;self.archive.write_bytes(data)
        with self.assertRaises(backup.BackupError):backup.restore(self.archive,self.destination,self.key,'erp-tur')
        self.assertFalse(self.destination.exists())
    def test_wrong_key_service_and_header_rejected(self):
        self.seal();other=self.root/'other.key';backup.keygen(other)
        for key,service in [(other,'erp-tur'),(self.key,'turismo')]:
            with self.assertRaises(backup.BackupError):backup.verify(self.archive,key,service)
        self.archive.write_bytes(self.archive.read_bytes().replace(b'erp-tur',b'turismo',1))
        with self.assertRaises(backup.BackupError):backup.verify(self.archive,self.key,'turismo')
    def test_nonce_randomness_prevents_identical_archives(self):
        self.seal();second=self.root/'second.sgacdb';backup.backup(self.source,second,self.key,'erp-tur')
        first=self.archive.read_bytes();other=second.read_bytes()
        import struct
        offset=len(backup.MAGIC)
        a=offset+4+struct.unpack('>I',first[offset:offset+4])[0]
        b=offset+4+struct.unpack('>I',other[offset:offset+4])[0]
        self.assertNotEqual(first[a:a+12],other[b:b+12])
    def test_existing_archive_and_destination_never_overwritten(self):
        self.seal();original=self.archive.read_bytes()
        with self.assertRaises(backup.BackupError):self.seal()
        self.assertEqual(self.archive.read_bytes(),original)
        self.destination.write_bytes(b'existing-data')
        with self.assertRaises(backup.BackupError):backup.restore(self.archive,self.destination,self.key,'erp-tur')
        self.assertEqual(self.destination.read_bytes(),b'existing-data')
    def test_wal_rows_are_included(self):
        with sqlite3.connect(self.source) as db:
            db.execute('PRAGMA journal_mode=WAL');db.execute('PRAGMA wal_autocheckpoint=0')
            db.execute('INSERT INTO documents(payload) VALUES (?)',('uncheckpointed-fixture',));db.commit()
            self.seal()
        backup.restore(self.archive,self.destination,self.key,'erp-tur')
        with sqlite3.connect(self.destination) as db:self.assertEqual(db.execute('SELECT count(*) FROM documents').fetchone()[0],2)
    def test_invalid_foreign_keys_not_certified(self):
        with sqlite3.connect(self.source) as db:
            db.execute('CREATE TABLE child(parent_id INTEGER REFERENCES documents(id))')
            db.execute('INSERT INTO child VALUES (999)')
        with self.assertRaises(backup.BackupError):self.seal()
        self.assertFalse(self.archive.exists())
    def test_permissions_symlink_and_sidecar_are_rejected(self):
        self.key.chmod(0o644)
        with self.assertRaises(backup.BackupError):self.seal()
        self.key.chmod(0o600);self.seal()
        self.destination.symlink_to(self.source)
        with self.assertRaises(backup.BackupError):backup.restore(self.archive,self.destination,self.key,'erp-tur')
        self.destination.unlink();Path(str(self.destination)+'-wal').write_bytes(b'old wal')
        with self.assertRaises(backup.BackupError):backup.restore(self.archive,self.destination,self.key,'erp-tur')
        self.assertFalse(self.destination.exists())
    def test_size_limit_rejects_before_archive_written(self):
        with patch.object(backup,'MAX_DATABASE',1):
            with self.assertRaises(backup.BackupError):self.seal()
        self.assertFalse(self.archive.exists())
    def test_truncated_and_malformed_archives_fail_safely(self):
        self.seal();original=self.archive.read_bytes()
        for data in [b'',original[:10],original[:20],original[:-40],backup.MAGIC+b'\xff'*4]:
            self.archive.write_bytes(data)
            with self.assertRaises(backup.BackupError):backup.verify(self.archive,self.key,'erp-tur')
    def test_partial_write_is_removed_without_touching_source(self):
        before=self.source.read_bytes()
        with patch.object(backup.os,'fsync',side_effect=OSError('fixture disk failure')):
            with self.assertRaises(OSError):self.seal()
        self.assertFalse(self.archive.exists());self.assertEqual(self.source.read_bytes(),before)
    def test_snapshot_deadline_and_repository_destinations_rejected(self):
        with patch.object(backup.time,'monotonic',side_effect=[0,61]):
            with self.assertRaises(backup.BackupError):self.seal()
        self.assertFalse(self.archive.exists())
        with self.assertRaises(backup.BackupError):backup.keygen(backup.ROOT/'must-not-create-backup-key.key')
        self.assertFalse((backup.ROOT/'must-not-create-backup-key.key').exists())

    def test_cli_does_not_print_secrets(self):
        self.seal();result=subprocess.run([sys.executable,str(Path(backup.__file__)),'verify','--key-file',str(self.key),'--archive',str(self.archive),'--service','erp-tur'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr);self.assertTrue(json.loads(result.stdout)['verified'])
        self.assertNotIn('private-fixture-content',result.stdout);self.assertNotIn(str(self.key),result.stdout)

if __name__=='__main__':unittest.main()
