"""Snapshot worktree changes and apply with content checks; never commit or push.
Archive extraction is explicit, bounded and rejects symlinks/private runtime paths.
"""
import argparse,hashlib,json,os,re,stat,subprocess,sys,tempfile,zipfile
from pathlib import Path,PurePosixPath

SCHEMA='sgacd-worktree-delivery-v1'
MAX_BYTES=64*1024*1024
FORBIDDEN={'.git','.runtime','.agents','.codex','.aws','.venv','venv','node_modules','__pycache__'}

def sha(data):return hashlib.sha256(data).hexdigest()

def relative(value):
    if not isinstance(value,str) or not value or '\\' in value or ':' in value:raise ValueError('Invalid relative path.')
    p=PurePosixPath(value)
    if p.is_absolute() or str(p)!=value or any(x.casefold() in FORBIDDEN or x in ('.','..') or x.rstrip(' .')!=x for x in p.parts) or p.name.casefold().startswith('.env') or p.suffix.lower() in {'.pem','.key','.sqlite','.sqlite3','.db','.zip','.pyz'}:raise ValueError('Unsafe or private runtime path.')
    return value

def target(root,value):
    p=root/relative(value)
    for part in [p,*p.parents]:
        if part==root.parent:break
        if part.is_symlink() or getattr(part,'is_junction',lambda:False)():raise ValueError('Symlink/junction paths are never followed.')
    if p.exists() and not p.is_file():raise ValueError('Target must be a regular file.')
    return p

def git(root,*args):return subprocess.run(['git','-C',str(root),*args],check=True,capture_output=True).stdout

def build(root,output):
    root=Path(root).resolve();output=Path(output).absolute()
    if output.exists():raise ValueError('Delivery already exists; do not overwrite a prior snapshot.')
    base=git(root,'rev-parse','HEAD').decode().strip()
    changes=git(root,'diff','--name-only','--no-renames','HEAD','-z')+git(root,'ls-files','--others','--exclude-standard','-z')
    names=sorted({x.decode('utf-8') for x in changes.split(b'\0') if x})
    excluded=[name for name in names if '__pycache__' in PurePosixPath(name).parts or PurePosixPath(name).suffix in {'.pyc','.pyo'}]
    paths=[relative(name) for name in names if name not in excluded]
    entries=[];blobs={};total=0
    for name in paths:
        path=target(root,name)
        try:original=git(root,'show',base+':'+name);base_hash=sha(original)
        except subprocess.CalledProcessError:base_hash=None
        data=path.read_bytes() if path.exists() else None
        if data is not None:
            if re.search(rb'(?m)^-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----\r?$',data):raise ValueError('Private-key material cannot be included.')
            total+=len(data)
            if total>MAX_BYTES:raise ValueError('Delivery exceeds its bounded size.')
            blobs['files/'+name]=data
        entries.append({'path':name,'base_sha256':base_hash,'sha256':sha(data) if data is not None else None,'size':len(data) if data is not None else 0,'mode':stat.S_IMODE(path.stat().st_mode)&0o777 if data is not None else None})
    if len(entries)>2000:raise ValueError('Too many delivery entries.')
    # Detect source changes during capture; the snapshot must not silently mix cuts.
    if git(root,'rev-parse','HEAD').decode().strip()!=base:raise ValueError('HEAD changed during capture.')
    for entry in entries:
        p=target(root,entry['path']);current=sha(p.read_bytes()) if p.exists() else None
        if current!=entry['sha256'] or p.exists() and stat.S_IMODE(p.stat().st_mode)&0o777!=entry['mode']:raise ValueError('Worktree changed during capture; create a fresh snapshot.')
    runner=Path(__file__).read_bytes()
    manifest={'excluded_generated_files':excluded,'runner_sha256':sha(runner),'schema':SCHEMA,'base_commit':base,'scope':'Modified/deleted tracked files plus nonignored untracked files; not repository history or runtime data','commits_created':False,'production_accepted':False,'entries':entries}
    output.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix='.sgacd-delivery-',dir=output.parent);temporary=Path(name)
    try:
        with os.fdopen(fd,'wb') as stream:
            with zipfile.ZipFile(stream,'w',compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr('manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2))
                archive.writestr('__main__.py',runner)
                for name,data in blobs.items():archive.writestr(name,data)
        os.link(temporary,output);temporary.unlink()
    except BaseException:
        temporary.unlink(missing_ok=True);raise
    return {'archive':str(output),'sha256':sha(output.read_bytes()),'base_commit':base,'files':len(entries),'excluded_generated_files':len(excluded),'bytes':total}

def load(archive):
    with zipfile.ZipFile(archive) as z:
        infos=z.infolist()
        if len(infos)>2002 or len({x.filename for x in infos})!=len(infos) or sum(x.file_size for x in infos)>MAX_BYTES+2*1024*1024:raise ValueError('Archive is duplicated or oversized.')
        info=z.getinfo('manifest.json')
        if info.file_size>2*1024*1024:raise ValueError('Manifest too large.')
        manifest=json.loads(z.read(info));entries=manifest.get('entries')
        if manifest.get('schema')!=SCHEMA or not isinstance(entries,list) or len(entries)>2000:raise ValueError('Unsupported delivery manifest.')
        seen=set();blobs={};members={'manifest.json','__main__.py'}
        if sha(z.read('__main__.py'))!=manifest.get('runner_sha256'):raise ValueError('Runner hash mismatch.')
        for entry in entries:
            if not isinstance(entry,dict) or set(entry)!={'path','base_sha256','sha256','size','mode'}:raise ValueError('Malformed delivery entry.')
            name=relative(entry['path'])
            if name in seen:raise ValueError('Duplicate delivery path.')
            seen.add(name)
            for key in ('base_sha256','sha256'):
                value=entry[key]
                if value is not None and (not isinstance(value,str) or len(value)!=64 or any(c not in '0123456789abcdef' for c in value)):raise ValueError('Invalid delivery hash.')
            if type(entry['size']) is not int or not 0<=entry['size']<=MAX_BYTES:raise ValueError('Invalid entry size.')
            if entry['sha256'] is None:
                if entry['size']!=0 or entry['mode'] is not None:raise ValueError('Invalid deletion record.')
                continue
            if type(entry['mode']) is not int or not 0<=entry['mode']<=0o777:raise ValueError('Invalid file mode.')
            member='files/'+name;members.add(member);info=z.getinfo(member)
            if stat.S_ISLNK(info.external_attr>>16):raise ValueError('Archive symlink rejected.')
            data=z.read(info)
            if len(data)!=entry['size'] or sha(data)!=entry['sha256']:raise ValueError('Payload hash/size mismatch.')
            blobs[name]=data
        if {x.filename for x in infos}!=members:raise ValueError('Unexpected archive members.')
        return manifest,blobs

def check(root,manifest):
    root=Path(root).resolve();rows=[]
    if not root.is_dir():raise ValueError('Destination must already exist.')
    for entry in manifest['entries']:
        path=target(root,entry['path']);current=sha(path.read_bytes()) if path.exists() else None
        mode_matches=os.name=='nt' or not path.exists() or stat.S_IMODE(path.stat().st_mode)&0o777==entry['mode']
        state='ALREADY_PRESENT' if current==entry['sha256'] and mode_matches else 'READY' if current==entry['base_sha256'] else 'CONFLICT'
        rows.append({'path':entry['path'],'state':state})
    return rows

def write_atomic(path,data,mode):
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix='.sgacd-delivery-',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as stream:stream.write(data);stream.flush();os.fsync(stream.fileno())
        os.chmod(name,mode);os.replace(name,path)
    finally:Path(name).unlink(missing_ok=True)

def apply(root,manifest,blobs):
    root=Path(root).resolve();rows=check(root,manifest)
    if any(x['state']=='CONFLICT' for x in rows):raise ValueError('Conflicts detected; nothing was applied. Preserve and review both versions.')
    pending=[e for e,r in zip(manifest['entries'],rows) if r['state']=='READY']
    if not pending:return {'applied':0,'already_present':len(rows),'backup':None}
    backup=Path(tempfile.mkdtemp(prefix='sgacd-delivery-backup-'));os.chmod(backup,0o700);originals={};written=[]
    for entry in pending:
        p=target(root,entry['path']);originals[entry['path']]=(p.read_bytes(),stat.S_IMODE(p.stat().st_mode)) if p.exists() else (None,None)
        if originals[entry['path']][0] is not None:
            destination=backup/'files'/entry['path'];destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(originals[entry['path']][0]);os.chmod(destination,0o600)
    journal={'schema':SCHEMA,'destination':str(root),'entries':pending,'original_modes':{name:mode for name,(_,mode) in originals.items()},'completed':[],'state':'PREPARED'}
    write_atomic(backup/'journal.json',json.dumps(journal,ensure_ascii=False,indent=2).encode(),0o600)
    try:
        for entry in pending:
            p=target(root,entry['path']);current=sha(p.read_bytes()) if p.exists() else None
            if current!=entry['base_sha256']:raise ValueError('Destination changed during application; preserving recovery backup.')
            if entry['sha256'] is None:p.unlink()
            else:write_atomic(p,blobs[entry['path']],entry['mode'])
            written.append(entry);journal['completed'].append(entry['path']);journal['state']='APPLYING';write_atomic(backup/'journal.json',json.dumps(journal,ensure_ascii=False,indent=2).encode(),0o600)
    except BaseException:
        conflicts=[]
        for entry in reversed(written):
            p=target(root,entry['path']);current=sha(p.read_bytes()) if p.exists() else None
            if current!=entry['sha256']:conflicts.append(entry['path']);continue
            data,mode=originals[entry['path']]
            if data is None:p.unlink(missing_ok=True)
            else:write_atomic(p,data,mode)
        journal.update(state='RECOVERY_REQUIRED' if conflicts else 'ROLLED_BACK',concurrent_changes=conflicts);write_atomic(backup/'journal.json',json.dumps(journal,ensure_ascii=False,indent=2).encode(),0o600)
        raise RuntimeError('Application interrupted; recovery journal retained at '+str(backup)) from None
    journal['state']='APPLIED';write_atomic(backup/'journal.json',json.dumps(journal,ensure_ascii=False,indent=2).encode(),0o600)
    return {'applied':len(pending),'already_present':len(rows)-len(pending),'backup':str(backup)}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('operation',choices=['build','check','apply']);parser.add_argument('--root',type=Path,required=True);parser.add_argument('--archive',type=Path);args=parser.parse_args()
    if args.archive is None:
        if args.operation=='build' or not sys.argv[0].endswith('.pyz'):parser.error('--archive is required when not checking/applying this .pyz delivery')
        args.archive=Path(sys.argv[0])
    if args.operation=='build':result=build(args.root,args.archive)
    else:
        manifest,blobs=load(args.archive)
        if args.operation=='apply':result=apply(args.root,manifest,blobs)
        else:
            rows=check(args.root,manifest);result={'files':len(rows),'ready':sum(r['state']=='READY' for r in rows),'already_present':sum(r['state']=='ALREADY_PRESENT' for r in rows),'conflicts':[r['path'] for r in rows if r['state']=='CONFLICT']}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 2 if result.get('conflicts') else 0
if __name__=='__main__':raise SystemExit(main())
