"""Encrypted SQLite recovery rehearsal into new private files; never replace a live DB.
Application signing/encryption keys, media volumes and external grants are excluded.
"""
import argparse,sys,json,time,os,sqlite3,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'deployment'))
from encrypted_backup import backup,verify,restore,SERVICES

def rehearse(source,directory,key_file,service):
 source=Path(source);directory=Path(directory)
 if service not in SERVICES:raise ValueError('Unsupported service')
 if directory.exists() or directory.is_symlink():raise ValueError('Use a new private destination')
 directory.mkdir(parents=True,mode=0o700,exist_ok=False)
 start=time.perf_counter();archive=directory/'database.sgacdb';target=directory/'restored.sqlite3'
 b=backup(source,archive,Path(key_file),service);v=verify(archive,Path(key_file),service);r=restore(archive,target,Path(key_file),service)
 with sqlite3.connect('file:'+str(target.resolve())+'?mode=ro',uri=True) as db:
  integrity=db.execute('PRAGMA integrity_check').fetchall();foreign=db.execute('PRAGMA foreign_key_check').fetchall();tables=db.execute("SELECT count(*) FROM sqlite_master WHERE type='table'").fetchone()[0]
 if integrity!=[('ok',)] or foreign:raise ValueError('Restored integrity review required')
 result={'service':service,'encrypted_backup_verified':v['verified'],'new_database_restored':r['restored_to_new_database'],'tables':tables,'foreign_keys_valid':True,'integrity_valid':True,'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'elapsed_seconds':round(time.perf_counter()-start,6),'live_database_replaced':False,'application_keys_included':False,'media_or_provider_restore_qualified':False,'production_rpo_rto_accepted':False}
 with open(directory/'report.json','x',opener=lambda p,f:os.open(p,f,0o600)) as stream:json.dump(result,stream,indent=2)
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--directory',type=Path,required=True);p.add_argument('--key-file',type=Path,required=True);p.add_argument('--service',choices=sorted(SERVICES),required=True);a=p.parse_args();print(json.dumps(rehearse(a.source,a.directory,a.key_file,a.service)))
