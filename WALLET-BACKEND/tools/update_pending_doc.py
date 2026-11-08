"""Generate the human production register from the canonical packaged registry."""
import argparse
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'WALLET-BACKEND/offline/src/sgacd_wallet_offline/production_pending.json'
TARGET=ROOT/'ANALISIS/produccion/PENDIENTES-PRODUCCION-BILLETERA.md'

def render():
    data=json.loads(SOURCE.read_text())
    rows=['# Pendientes de producción de la billetera','','Producción: **NO HABILITADA**. Registro vivo; una prueba sintética no cierra validaciones físicas o de proveedores.','','Actualizar el JSON canónico en `WALLET-BACKEND/offline/src/sgacd_wallet_offline/production_pending.json` y ejecutar `python WALLET-BACKEND/tools/update_pending_doc.py` en cada entrega. Cerrar solo con evidencia verificable, responsable y criterio de aceptación satisfecho.','','Sin internet se permiten apuntes y borradores cifrados. No hay liquidación entre cuentas, retiros o depósitos fuera del servidor. Las dos revisiones locales no son firmas financieras ni permisos de control.','']
    for item in data['items']:
        rows.extend([f"## {item['id']} · {item['title']}",'',f"Estado: **{item['status']}** · Área: {item['area']} · Responsable: {item['owner']}",'',item['acceptance'],'','Evidencia: '+item['evidence'],''])
    return '\n'.join(rows)+'\n'
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args();text=render()
    if args.check:
        if not TARGET.exists() or TARGET.read_text()!=text:raise SystemExit('Production pending document is stale')
    else:TARGET.write_text(text)
