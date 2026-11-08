"""Private Linux/PostgreSQL HTTP contract. Imported only by the isolated PG fixture."""
import json,os,secrets,sys,time,types,uuid
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from urllib.request import build_opener,HTTPCookieProcessor,Request,ProxyHandler
from urllib.error import HTTPError
from http.cookiejar import CookieJar


def serve(pipe,clock):
    from unittest.mock import patch
    from django.db import connections
    from django.core.handlers.wsgi import WSGIHandler
    from wsgiref.simple_server import make_server,WSGIRequestHandler
    class Quiet(WSGIRequestHandler):
        def log_message(self,*args):pass
    connections.close_all()
    app=WSGIHandler()
    def application(environ,start_response):
        def start(status,headers,exc_info=None):
            return start_response(status,headers+[('X-Test-Worker',str(os.getpid()))],exc_info)
        return app(environ,start)
    with patch('time.time',side_effect=lambda:clock.value):
        server=make_server('127.0.0.1',0,application,handler_class=Quiet)
        pipe.send(server.server_port);pipe.close()
        try:server.serve_forever(poll_interval=.1)
        finally:server.server_close();connections.close_all()


def run(context):
    from django.test import override_settings
    from django.db import connections
    from django.urls import path,clear_url_caches
    from api.models import CustomUser
    from allauth.mfa.totp.internal.auth import TOTP,generate_totp_secret,hotp_value,format_hotp_value
    from allauth.mfa.recovery_codes.internal.auth import RecoveryCodes
    from apps.turismo.models import ErpSecurityEvent,ErpTotpUsage
    from apps.prestadores.mi_negocio.web_session import SessionStatus,SessionLogin,SessionMfa,SessionRecovery,RecoveryIssue
    module=types.ModuleType('mfa_http_fixture_urls')
    base='api/v1/erp-session/'
    module.urlpatterns=[path(base,SessionStatus.as_view()),path(base+'login/',SessionLogin.as_view()),path(base+'mfa/',SessionMfa.as_view()),path(base+'recovery/',SessionRecovery.as_view()),path(base+'recovery/issue/',RecoveryIssue.as_view())]
    sys.modules[module.__name__]=module
    settings=override_settings(ROOT_URLCONF=module.__name__,MIDDLEWARE=['django.contrib.sessions.middleware.SessionMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware'],ERP_WEB_SESSION_ENABLED=True,ERP_RECOVERY_CODES_ENABLED=True,ERP_RECOVERY_ISSUANCE_ENABLED=True,SESSION_COOKIE_SECURE=False,CSRF_COOKIE_SECURE=False,ALLOWED_HOSTS=['127.0.0.1'],CSRF_TRUSTED_ORIGINS=[],SECURE_SSL_REDIRECT=False)
    settings.enable();clear_url_caches()
    clock=context.Value('d',time.time());workers=[];ports=[];results=[]
    def client():return build_opener(ProxyHandler({}),HTTPCookieProcessor(CookieJar()))
    def request(browser,index,route='',data=None,csrf=None):
        origin='http://127.0.0.1:'+str(ports[index]);headers={'Content-Type':'application/json','Origin':origin}
        if csrf:headers['X-CSRFToken']=csrf
        message=Request(origin+'/'+base+route,data=json.dumps(data).encode() if data is not None else None,headers=headers)
        try:response=browser.open(message,timeout=15)
        except HTTPError as error:response=error
        with response:
            body=json.loads(response.read());return response.status,body.get('data',body),response.headers.get('X-Test-Worker')
    def fixture():
        password=secrets.token_urlsafe(24);user=CustomUser(username='synthetic-http-'+uuid.uuid4().hex,role='BUSINESS_OWNER');user.set_password(password);CustomUser.objects.bulk_create([user])
        secret=generate_totp_secret();factor=TOTP.activate(user,secret).instance
        return user,password,secret,factor
    def code(secret):return format_hotp_value(hotp_value(secret,int(clock.value)//30))
    def login(browser,index,user,password):
        status,state,_=request(browser,index);assert status==200
        status,pending,_=request(browser,index,'login/',{'username':user.username,'password':password},state['csrf_token'])
        assert status==202 and not pending['authenticated'];return pending
    def race(browsers,route,payloads,tokens):
        barrier=Barrier(2)
        def attempt(index):
            barrier.wait(timeout=10);return request(browsers[index],index,route,payloads[index],tokens[index])
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(attempt,index) for index in (0,1)];outcomes=[future.result(timeout=20) for future in futures]
        assert len({outcome[2] for outcome in outcomes})==2
        return outcomes
    try:
        for _ in (0,1):
            connections.close_all();parent,child=context.Pipe(duplex=False)
            process=context.Process(target=serve,args=(child,clock));process.start();child.close();workers.append(process)
            if not parent.poll(15):raise RuntimeError('HTTP fixture did not start')
            ports.append(parent.recv());parent.close()
        for recovery in (False,True):
            user,password,secret,factor=fixture();backup=RecoveryCodes.activate(user) if recovery else None
            proof=backup.get_unused_codes()[0] if backup else code(secret)
            browsers=[client(),client()];pending=[login(browsers[i],i,user,password) for i in (0,1)]
            # A real HTTP POST without CSRF must fail before consuming the challenge.
            status,_,_=request(browsers[0],0,'recovery/' if recovery else 'mfa/',{'challenge_id':pending[0]['challenge_id'],'code':proof});assert status==403
            outcomes=race(browsers,'recovery/' if recovery else 'mfa/',[{'challenge_id':item['challenge_id'],'code':proof} for item in pending],[item['csrf_token'] for item in pending])
            assert sorted(item[0] for item in outcomes)==[200,403]
            winner=next(index for index,item in enumerate(outcomes) if item[0]==200)
            # Session established by one worker must be readable by the other.
            status,state,_=request(browsers[winner],1-winner);assert status==200 and state['authenticated']
            if recovery:
                backup.instance.refresh_from_db();assert backup.instance.data['used_mask']==1
                assert ErpSecurityEvent.objects.filter(actor_id=user.pk,kind='recovery_used').count()==1
            else:assert ErpTotpUsage.objects.get(factor=factor).last_counter==int(clock.value)//30
            results.append({'scenario':'http_recovery' if recovery else 'http_totp','workers':2,'accepted':1,'rejected':1,'csrf_enforced':True,'session_shared_across_workers':True})
        user,password,secret,factor=fixture();browsers=[client(),client()]
        for index in (0,1):
            pending=login(browsers[index],index,user,password)
            status,state,_=request(browsers[index],index,'mfa/',{'challenge_id':pending['challenge_id'],'code':code(secret)},pending['csrf_token']);assert status==200
            clock.value+=30
        states=[request(browsers[i],i)[1] for i in (0,1)]
        outcomes=race(browsers,'recovery/issue/',[{'password':password,'code':code(secret)} for _ in (0,1)],[state['csrf_token'] for state in states])
        assert sorted(item[0] for item in outcomes)==[201,403]
        accepted=next(item[1] for item in outcomes if item[0]==201)
        assert RecoveryCodes(RecoveryCodes.activate(user).instance).get_unused_codes()==accepted['codes']
        assert ErpSecurityEvent.objects.filter(actor_id=user.pk,kind='recovery_issued').count()==1
        assert ErpTotpUsage.objects.get(factor=factor).last_counter==int(clock.value)//30
        results.append({'scenario':'http_issuance','workers':2,'accepted':1,'rejected':1,'audit_events':1})
        return results
    finally:
        for process in workers:
            process.terminate();process.join(timeout=5)
            if process.is_alive():process.kill();process.join(timeout=5)
        connections.close_all();settings.disable();clear_url_caches();sys.modules.pop(module.__name__,None)
