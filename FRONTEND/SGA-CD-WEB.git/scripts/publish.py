"""Update the existing demo web copy; preserve configuration and reject conflicts."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import shutil
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from render_landing import render

parser = argparse.ArgumentParser()
parser.add_argument('--demo-dir', type=Path, default=Path.home() / 'sgacd-demo')
parser.add_argument('--check', action='store_true', help='Validate source and conflicts without writing files')
args = parser.parse_args()
repo = Path(__file__).resolve().parents[3]
published = args.demo_dir.resolve() / 'web'
manifest = json.loads((repo / 'FRONTEND/SGA-CD-WEB.git/deployment/manifest.json').read_text())
if not published.is_dir():
    raise SystemExit('No se encontró la copia web de la demo: ' + str(published))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None

state_path = args.demo_dir.resolve() / "web-deployment.json"
state = json.loads(state_path.read_text()) if state_path.exists() else {}
new_state = {}
changes = []
for name, entry in manifest.items():
    source = repo / 'FRONTEND/SGA-CD-WEB.git' / name
    target = published / name
    if not target.resolve().is_relative_to(published):
        raise SystemExit('Ruta publicada inesperada: ' + name)
    if digest(source) != entry['after']:
        raise SystemExit('El código cambió después de preparar la entrega: ' + name)
    payload = render(repo / 'FRONTEND/SGA-CD-WEB.git', published) if name == 'index.html' else source.read_bytes()
    desired = hashlib.sha256(payload).hexdigest()
    new_state[name] = desired
    actual = digest(target)
    if actual == desired:
        continue
    accepted = entry.get('accepted', [entry['before']]) + [entry['after']]
    if name in state:
        accepted = accepted + [state[name]]
    if actual not in accepted:
        raise SystemExit('Conflicto en ' + str(target) + '. No se modificó ningún archivo.')
    changes.append((payload, target, name))

# Publish the single canonical assistance interface on this site's own JWT origin.
for name in ['assistance.html', 'js/assistance.js', 'css/assistance.css', 'control.html', 'js/control.js']:
    source = repo / 'FRONTEND/ANALEMATICA-FRONTEND' / name
    target = published / name
    if source.is_symlink() or not source.is_file() or not target.resolve().is_relative_to(published):
        raise SystemExit('Recurso de asistencia no permitido: ' + name)
    payload = source.read_bytes()
    desired = hashlib.sha256(payload).hexdigest()
    new_state[name] = desired
    actual = digest(target)
    if actual == desired:
        continue
    if actual is not None and actual != state.get(name):
        raise SystemExit('Archivo de asistencia personalizado; no se sobrescribió: ' + name)
    changes.append((payload, target, name))

if args.check:
    print('Verificación web correcta; archivos previstos:', len(changes))
    raise SystemExit(0)

stamp = datetime.now(timezone.utc).strftime('%Y-%m-%d/respaldo-web-%H%M%S-%f')
backup = repo / 'FRONTEND/SGA-CD-WEB.git' / 'deployment' / 'backups' / stamp
for payload, target, name in changes:
    if target.exists():
        saved = backup / name
        saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, saved)
for payload, target, name in changes:
    target.parent.mkdir(parents=True, exist_ok=True)
    for parent in target.parents:
        if parent == published:
            break
        parent.chmod(0o755)
    target.write_bytes(payload)
    target.chmod(0o644)
state_path.write_text(json.dumps(new_state, indent=2) + '\n')
print('Archivos web actualizados:', len(changes))
if changes:
    print('Respaldo:', backup)
print('Se conservaron js/config.js, credenciales y datos. Recarga con Ctrl+Shift+R.')
