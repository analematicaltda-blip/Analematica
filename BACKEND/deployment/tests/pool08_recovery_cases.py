"""Restore actual commercial state/audit tables and reject a corrupt archive/key."""
import sqlite3,tempfile,runpy,json,hashlib
from pathlib import Path
class RecoveryCases:
 def test_actual_commercial_database_restored_without_overwrite(self):
  self.setup_ops();ref=self.mission();trace=self.ops.trace('army',ref);root=Path(__file__).resolve().parents[3];recovery=runpy.run_path(str(root/'BACKEND/INTEGRACIONES/operacion/commercial_recovery.py'),run_name='recovery_fixture');from encrypted_backup import keygen,verify,BackupError
  with tempfile.TemporaryDirectory(prefix='commercial-recovery-') as folder:
   folder=Path(folder);source=folder/'source.sqlite3';key=folder/'backup.key';keygen(key)
   if self.module.SYSTEM=='sga-cd':
    table='sga_army_job';connection=self.gen.crm.store.db.connection().connection.driver_connection
   else:
    from django.db import connection as django_connection
    connection=django_connection.connection;table=('erp' if self.module.SYSTEM=='erp-tur' else 'ana')+'_army_job'
   with sqlite3.connect(source) as target:connection.backup(target)
   before=hashlib.sha256(source.read_bytes()).hexdigest();r=recovery['rehearse'](source,folder/'candidate',key,'sgacd' if self.module.SYSTEM=='sga-cd' else self.module.SYSTEM);self.assertTrue(r['new_database_restored']);self.assertFalse(r['live_database_replaced']);self.assertFalse(r['production_rpo_rto_accepted']);self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),before)
   with sqlite3.connect(folder/'candidate/restored.sqlite3') as db:
    d=json.loads(db.execute('SELECT document FROM '+table+' WHERE id=?',(ref,)).fetchone()[0]);self.assertEqual(self.module.digest(d),trace['state_digest']);self.assertEqual(d['last_event_digest'],trace['events'][-1]['event_digest'])
   with self.assertRaises(ValueError):recovery['rehearse'](source,folder/'candidate',key,'sgacd' if self.module.SYSTEM=='sga-cd' else self.module.SYSTEM)
   wrong=folder/'wrong.key';keygen(wrong)
   with self.assertRaises(BackupError):verify(folder/'candidate/database.sgacdb',wrong,'sgacd' if self.module.SYSTEM=='sga-cd' else self.module.SYSTEM)
