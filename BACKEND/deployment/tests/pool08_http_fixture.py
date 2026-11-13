"""Disposable ASGI contract/gateway harness. Not a deployment entry point."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import runpy
import socket
import sys
import uvicorn

parser=argparse.ArgumentParser()
parser.add_argument('--system',choices=['sga-cd','gateway'],required=True)
parser.add_argument('--directory',type=Path,required=True)
parser.add_argument('--native-origin',default='')
args=parser.parse_args()
root=Path(__file__).resolve().parents[3]
if args.system=='sga-cd':
    fixtures=runpy.run_path(str(Path(__file__).resolve().parents[3] / 'BACKEND/tests/workspace/test_workspace.py'),run_name='pool08_sga_http_fixture')
    case=fixtures['WorkspaceTests']();case.setUp()
    from app.commercial.pool08.api import router
    case.client.app.include_router(router,prefix='/api/v1/commercial-unified')
    from app.commercial.pool08.install_crm import install
    install(case.engine,apply=True)
    if os.environ.get('GC014_VIDEO_FIXTURE')=='1':
        from app.commercial.pool08.video_composition import fingerprint
        from app.models.user import Usuario
        from app.commercial.pool08.crm_api import service
        from types import SimpleNamespace
        from starlette.datastructures import QueryParams
        crm=service(SimpleNamespace(method='POST',query_params=QueryParams()),case.db,case.db.get(Usuario,case.users['full-admin_empresa']))
        key='sga-cd:'+crm.store.scope+':-'
        os.environ['COMMERCIAL_GENERATION_PROFILES']=json.dumps({key:{'video':{'adapter':'ffmpeg-composition','model':'ffmpeg-composition-v1','model_digest':fingerprint(),'rights_note':'Synthetic HTTP fixture only','cost_units':100,'max_output_tokens':64}}})
    if os.environ.get('GC016_EMAIL_FIXTURE')=='1':
        from app.models.user import Usuario
        email_key='sga-cd:'+('tenant:'+str(case.db.get(Usuario,case.users['full-admin_empresa']).inquilino_id))+':-'
        os.environ['COMMERCIAL_EMAIL_POLICIES']=json.dumps({email_key:{'version':'fixture-1','sender_email':'owner@example.test','sender_name':'Empresa sintética','postal_address':'Dirección de laboratorio','public_base_url':'http://localhost','daily_limit':10,'consent_reviewed':True,'allow_dispatch':False,'smtp_host':'127.0.0.1','smtp_port':1025}})
        os.environ['COMMERCIAL_EMAIL_LINK_KEYS']=json.dumps({email_key:'synthetic-email-fixture-key-only-32'})
    if os.environ.get('GC017_MOBILE_FIXTURE')=='1':
        from app.models.user import Usuario
        from mobile_message_fixture import configure
        configure('sga-cd','tenant:'+str(case.db.get(Usuario,case.users['full-admin_empresa']).inquilino_id))
    if os.environ.get('GC018_PUBLISH_FIXTURE')=='1':
        from app.models.user import Usuario
        from publishing_fixture import configure
        configure('sga-cd','tenant:'+str(case.db.get(Usuario,case.users['full-admin_empresa']).inquilino_id))
    if os.environ.get('GC019_INBOX_FIXTURE')=='1':
        from app.models.user import Usuario
        from inbox_fixture import configure
        configure('sga-cd','tenant:'+str(case.db.get(Usuario,case.users['full-admin_empresa']).inquilino_id))
    if os.environ.get('GC020_ADS_FIXTURE')=='1':
        from app.models.user import Usuario
        from ads_fixture import configure
        configure('sga-cd','tenant:'+str(case.db.get(Usuario,case.users['full-admin_empresa']).inquilino_id))
    application=case.client.app
    credentials={'token':case.client.headers['Authorization'][7:],'actor_ref':str(case.users['full-admin_empresa'])}
    from app.models.workspace import WorkspaceGrant
    staff_id=case.users['full-jefe_area']
    case.db.query(WorkspaceGrant).filter_by(user_id=staff_id,permission='crm').update({'enabled':True});case.db.commit()
    case.login('full-jefe_area');credentials['staff_token']=case.client.headers['Authorization'][7:];credentials['staff_ref']=str(staff_id)
    case.login('other-admin_empresa');credentials['other_token']=case.client.headers['Authorization'][7:]
    case.login('full-admin_empresa')
    with open(args.directory/'sga.json','x',opener=lambda p,f:os.open(p,f,0o600)) as stream:json.dump(credentials,stream)
else:
    os.environ['SGACD_API_URL']='http://127.0.0.1:1'
    os.environ['ANALEMATICA_COMMERCIAL_API_URL']=args.native_origin
    spec=importlib.util.spec_from_file_location('pool08_gateway',root/'BACKEND/ANALEMATICA-BACKEND/deployment/api.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);application=module.app
sock=socket.socket();sock.bind(('127.0.0.1',0));sock.listen(128)
print('READY '+str(sock.getsockname()[1]),flush=True)
try:
    uvicorn.Server(uvicorn.Config(application,log_level='error',access_log=False)).run(sockets=[sock])
finally:
    sock.close()
    if args.system=='sga-cd':case.tearDown()
