"""Update the existing demo web copy; preserve configuration and reject conflicts."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import shutil

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

changes = []
for name, entry in manifest.items():
    source = repo / 'SGA-CD-WEB.git' / name
    target = published / name
    if not target.resolve().is_relative_to(published):
        raise SystemExit('Ruta publicada inesperada: ' + name)
    if digest(source) != entry['after']:
        raise SystemExit('El código cambió después de preparar la entrega: ' + name)
    actual = digest(target)
    if actual == entry['after']:
        continue
    if actual not in entry.get('accepted', [entry['before']]):
        raise SystemExit('Conflicto en ' + str(target) + '. No se modificó ningún archivo.')
    changes.append((source, target, name))

stamp = datetime.now(timezone.utc).strftime('%Y-%m-%d/respaldo-web-%H%M%S-%f')
backup = repo / 'verificaciones' / stamp
for source, target, name in changes:
    if target.exists():
        saved = backup / name
        saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, saved)
for source, target, name in changes:
    target.parent.mkdir(parents=True, exist_ok=True)
    for parent in target.parents:
        if parent == published:
            break
        parent.chmod(0o755)
    shutil.copy2(source, target)
    target.chmod(0o644)
print('Archivos web actualizados:', len(changes))
if changes:
    print('Respaldo:', backup)
print('Se conservaron js/config.js, credenciales y datos. Recarga con Ctrl+Shift+R.')
