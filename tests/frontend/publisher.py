"""Exercise deployment safety against a disposable published copy."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tempfile

repo=Path(__file__).resolve().parents[2]
source=repo/'FRONTEND/SGA-CD-WEB.git'
manifest=json.loads((repo/'scripts/flet_preview/web-manifest.json').read_text())
original=(source/'index.html').read_bytes()
with tempfile.TemporaryDirectory() as tmp:
    demo=Path(tmp); web=demo/'web'; web.mkdir()
    for name in manifest:
        target=web/name; target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source/name,target)
    (web/'js/config.js').write_text('const config = {apiBaseUrl: window.location.origin};')
    config=(web/'js/config.js').read_bytes()
    command=['python3',str(repo/'scripts/update_demo_web.py'),'--demo-dir',str(demo)]
    subprocess.run(command,check=True,capture_output=True)
    first=(web/'index.html').read_bytes()
    assert first!=original
    assert (source/'index.html').read_bytes()==original
    assert (web/'js/config.js').read_bytes()==config
    second=subprocess.run(command,check=True,capture_output=True,text=True)
    assert 'actualizados: 0' in second.stdout
    assert (web/'index.html').read_bytes()==first
    (web/'css/sky-theme.css').write_text('/* local edit */')
    before={name:hashlib.sha256((web/name).read_bytes()).hexdigest() for name in manifest}
    conflict=subprocess.run(command,capture_output=True,text=True)
    assert conflict.returncode!=0 and 'Conflicto' in conflict.stderr
    assert before=={name:hashlib.sha256((web/name).read_bytes()).hexdigest() for name in manifest}
print('PASS publisher: deterministic, config/template preserved, repeated deploy unchanged, conflicts abort without writes')
