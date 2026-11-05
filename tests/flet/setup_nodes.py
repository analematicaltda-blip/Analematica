"""Verify adding and repeating node setup preserves the existing demo."""
from pathlib import Path
import json
import subprocess
import tempfile

repo=Path(__file__).resolve().parents[2]
with tempfile.TemporaryDirectory() as directory:
    demo=Path(directory); compose=demo/'compose.json'
    initial={'services':{'postgres':{'image':'postgres:15-alpine','volumes':['db:/var/lib/postgresql/data']}},'volumes':{'db':{},'flet-desktop_state':{'external':True}}}
    compose.write_text(json.dumps(initial))
    command=['python3',str(repo/'scripts/setup_flet_previews.py'),'--demo-dir',directory]
    subprocess.run(command,check=True,capture_output=True)
    added=json.loads(compose.read_text())
    assert added['services']['postgres']==initial['services']['postgres']
    assert added['volumes']['db']=={}
    assert added['volumes']['flet-desktop_state']=={'external':True}
    for service,folder,port in [('flet-desktop','DESKTOP/SGA-CD-APP.git',8501),('flet-mobile','MOVILES/SGA-CD-APK.git',8502)]:
        node=added['services'][service]
        assert node['ports']==[f'127.0.0.1:{port}:{port}']
        assert str(repo/folder)+':/client:ro' in node['volumes']
    before=compose.read_bytes()
    subprocess.run(command,check=True,capture_output=True)
    assert compose.read_bytes()==before
    assert len(list(demo.glob('compose.before-flet-*.json')))==1
    # An existing deployment may still reference the former root-level source folders.
    legacy=json.loads(compose.read_text())
    sentinel=demo/'offline-sentinel.sqlite';sentinel.write_bytes(b'offline-state-preserved')
    for service,folder in [('flet-desktop','DESKTOP/SGA-CD-APP.git'),('flet-mobile','MOVILES/SGA-CD-APK.git')]:
        legacy['services'][service]['volumes']=[str(repo/Path(folder).name)+':/client:ro' if mount==str(repo/folder)+':/client:ro' else mount for mount in legacy['services'][service]['volumes']]
    compose.write_text(json.dumps(legacy))
    subprocess.run(command,check=True,capture_output=True)
    assert json.loads(compose.read_text())==added
    assert sentinel.read_bytes()==b'offline-state-preserved'
    assert len(list(demo.glob('compose.before-flet-*.json')))==2
    added['services']['flet-mobile']['ports']=['127.0.0.1:9999:8502']
    compose.write_text(json.dumps(added)); before=compose.read_bytes()
    dockerfile=demo/'flet-image/Dockerfile'; dockerfile.write_text('# local edit')
    result=subprocess.run(command,capture_output=True)
    assert result.returncode!=0
    assert compose.read_bytes()==before and dockerfile.read_text()=='# local edit'
print('PASS Flet setup: correct folders/private bindings, existing database preserved, repeat safe, custom configuration rejected')
