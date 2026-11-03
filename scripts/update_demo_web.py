"""Update the existing demo web copy; preserve configuration and reject conflicts."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import shutil
from render_landing import render

parser = argparse.ArgumentParser()
parser.add_argument('--demo-dir', type=Path, default=Path.home() / 'sgacd-demo')
args = parser.parse_args()
repo = Path(__file__).resolve().parent.parent
published = args.demo_dir.resolve() / 'web'
manifest = json.loads((repo / 'scripts/flet_preview/web-manifest.json').read_text())
if not published.is_dir():
    raise SystemExit('No se encontró la copia web de la demo: ' + str(published))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None

state_path = args.demo_dir.resolve() / "web-deployment.json"
state = json.loads(state_path.read_text()) if state_path.exists() else {}
new_state = {}
changes = []
for name, entry in manifest.items():
    source = repo / 'SGA-CD-WEB.git' / name
    target = published / name
    if not target.resolve().is_relative_to(published):
        raise SystemExit('Ruta publicada inesperada: ' + name)
    if digest(source) != entry['after']:
        raise SystemExit('El código cambió después de preparar la entrega: ' + name)
    payload = render(repo / 'SGA-CD-WEB.git', published) if name == 'index.html' else source.read_bytes()
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

stamp = datetime.now(timezone.utc).strftime('%Y-%m-%d/respaldo-web-%H%M%S-%f')
backup = repo / 'verificaciones' / stamp
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
