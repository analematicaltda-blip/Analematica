"""Create one test owner only in this Compose stack's new local database."""
import argparse
import json
import os
from pathlib import Path
import secrets
import subprocess

REMOTE = r'''
import json,sys
from app.db.session import engine,SessionLocal
from app.models.user import Usuario,Role,RolesEnum
from app.models.tenancy import Inquilino
from app.models.corporate import CorporateOwner
from app.core.security import get_password_hash,verify_password
if engine.url.host != 'sgacd-db' or engine.url.database != 'sgacd':
    raise SystemExit('Refused: this helper only targets the isolated local sgacd database.')
credentials=json.load(sys.stdin)
with SessionLocal() as db:
    user=db.query(Usuario).filter_by(nombre_usuario=credentials['username']).first()
    owner=db.get(CorporateOwner,1)
    if owner and (not user or owner.user_id != user.id):
        raise SystemExit('An owner already exists; no account or password was changed.')
    if user:
        if not verify_password(credentials['password'],user.password_hash):
            raise SystemExit('Existing account does not match the private local access file; password unchanged.')
    else:
        for role in RolesEnum:
            if not db.query(Role).filter_by(nombre=role.value).first():
                db.add(Role(nombre=role.value,descripcion='Rol local de pruebas'))
        db.flush()
        tenant=Inquilino(nombre_empresa='Laboratorio local SGA-CD',activo=True)
        db.add(tenant);db.flush()
        user=Usuario(nombre_usuario=credentials['username'],correo='owner@local.example.invalid',nombre_completo='Dueño de pruebas locales',password_hash=get_password_hash(credentials['password']),rol=RolesEnum.admin_general,inquilino_id=tenant.id,activo=True)
        user.roles.append(db.query(Role).filter_by(nombre='admin_general').one())
        db.add(user);db.flush()
    if not owner:db.add(CorporateOwner(id=1,user_id=user.id))
    db.commit()
print('Local test owner prepared; no credentials printed or preexisting owner changed.')
'''

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', default='sgacd-backends')
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[2]
    directory=root/'FRONTEND/deployment/private'
    directory.mkdir(mode=0o700,parents=True,exist_ok=True)
    path=directory/'application-access.json'
    if path.exists():credentials=json.loads(path.read_text())
    else:
        credentials={'username':'local_owner','password':secrets.token_urlsafe(24)}
        with open(path,'x',opener=lambda name,flags:os.open(name,flags,0o600)) as stream:json.dump(credentials,stream)
    subprocess.run(['docker','compose','-p',args.project,'-f',str(Path(__file__).parent/'compose.yaml'),'exec','-T','sgacd','python','-c',REMOTE],input=json.dumps(credentials).encode(),check=True)
    report=directory/'LOGIN-APLICACIONES.md'
    with open(report,'w',opener=lambda name,flags:os.open(name,flags,0o600)) as stream:
        stream.write('# Login privado de las aplicaciones locales\n\nSGA-CD y Analemática comparten la cuenta de dueño en la base nueva de pruebas.\n\nUsuario: '+credentials['username']+'\nClave: '+credentials['password']+'\n\nERP y Turismo no tienen un login funcional validado: sus backends siguen bloqueados.\nLas claves de ACCESOS-LOCALES.md abren solamente las vistas de revisión.\n')
    print('Login guardado en FRONTEND/deployment/private/LOGIN-APLICACIONES.md.')

if __name__=='__main__':main()
