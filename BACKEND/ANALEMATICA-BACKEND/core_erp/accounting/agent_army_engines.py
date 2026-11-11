"""Explicit, separately scoped local engine adapters. Never financial executors."""
import hashlib,json,os,re,subprocess,threading
from pathlib import Path
from urllib.parse import urlsplit
import httpx
from rest_framework.exceptions import PermissionDenied,ValidationError

class EngineUnavailable(Exception):pass
class EngineOutcomeUnknown(Exception):pass


def configured(policy):
    return {engine:{'enabled':os.environ.get(policy.prefix+'_'+suffix+'_ENABLED')=='1',
                    'readiness':'NOT_PROBED','scope':'PLAN_ONLY' if engine=='open-duet' else 'STATUS_ONLY'}
            for engine,suffix in [('open-duet','DUET'),('agent-desktop','DESKTOP')]}


def configuration(policy,actor,company,engine):
    if engine not in ('open-duet','agent-desktop'):raise ValidationError('Motor no permitido.')
    suffix='DUET' if engine=='open-duet' else 'DESKTOP';prefix=policy.prefix+'_'+suffix
    if os.environ.get(prefix+'_ENABLED')!='1':raise EngineUnavailable('Local engine is disabled.')
    if os.environ.get(prefix+'_OWNER_ID')!=str(actor.pk) or os.environ.get(prefix+'_COMPANY_ID')!=str(company.pk):
        raise PermissionDenied('El motor local no está asignado a este administrador y empresa.')
    if engine=='open-duet':
        origin=os.environ.get(prefix+'_ORIGIN','');token=os.environ.get(prefix+'_TOKEN','');provider=os.environ.get(prefix+'_PROVIDER','')
        try:
            url=urlsplit(origin)
            valid=(url.scheme=='http' and url.hostname in {'127.0.0.1','localhost','::1'} and url.port is not None
                   and url.path in ('','/') and not(url.username or url.password or url.query or url.fragment))
        except ValueError:valid=False
        if not valid or not 16<=len(token)<=4096 or any(ord(c)<33 or ord(c)>126 for c in token) or not re.fullmatch('[a-z][a-z0-9_-]{0,31}',provider):
            raise EngineUnavailable('Invalid local planning-engine configuration.')
        return {'origin':origin.rstrip('/'),'token':token,'provider':provider}
    binary=Path(os.environ.get(prefix+'_BINARY',''))
    expected=os.environ.get(prefix+'_SHA256','')
    if not binary.is_absolute() or binary.is_symlink() or not binary.is_file() or any(p.is_symlink() for p in binary.parents) or binary.stat().st_size>64*1024*1024 or not re.fullmatch('[0-9a-f]{64}',expected):
        raise EngineUnavailable('Pinned local runtime required.')
    if hashlib.sha256(binary.read_bytes()).hexdigest()!=expected:raise EngineUnavailable('Runtime integrity mismatch.')
    return {'binary':str(binary),'sha256':expected}


def strict_json(raw):
    def pairs(items):
        result={}
        for k,v in items:
            if k in result:raise ValueError('Duplicate engine field.')
            result[k]=v
        return result
    def reject(value):raise ValueError('Nonfinite engine number.')
    value=json.loads(raw,object_pairs_hook=pairs,parse_constant=reject)
    if not isinstance(value,dict):raise ValueError('Engine object required.')
    return value


def duet_plan(config,plan,transport=None):
    """Only static task names/statuses; no balances, documents, actors or credentials."""
    with httpx.Client(base_url=config['origin'],headers={'Authorization':'Bearer '+config['token']},
                      timeout=10,follow_redirects=False,trust_env=False,transport=transport) as client:
        def post(path,body):
            with client.stream('POST','/api/v1'+path,json=body) as response:
                if response.status_code not in (200,201,202) or response.is_redirect or response.headers.get('content-encoding','identity')!='identity':raise EngineOutcomeUnknown('Planning response not verified.')
                raw=bytearray()
                for chunk in response.iter_bytes(4096):
                    raw.extend(chunk)
                    if len(raw)>32768:raise EngineOutcomeUnknown('Planning response exceeds bound.')
                try:return strict_json(raw)
                except (ValueError,TypeError,RecursionError):raise EngineOutcomeUnknown('Planning response not verified.') from None
        def key(value):
            if type(value.get('id')) is not int or value['id']<=0:raise EngineOutcomeUnknown('Planning identifier missing.')
            return value['id']
        try:
            agent=post('/agents',{'name':'Ejército contable · '+plan['system'],'title':'Revisión contable supervisada',
                'description':'Planificación sin operaciones financieras','instructions':plan['instruction'],
                'provider':config['provider'],'approval_mode':'plan','make_lead':False,'memory_enabled':False,
                'recall_enabled':False,'memory_upkeep':False,'compaction_summary':False,'use_helper':False})
            if agent.get('approval_mode')!='plan' or agent.get('memory_enabled') is not False:raise EngineOutcomeUnknown('Engine did not confirm plan-only mode.')
            agent_id=key(agent);thread_id=key(post('/threads',{'agent_id':agent_id,'provider':config['provider'],'title':'Revisión de tareas contables'}))
            turn_id=key(post('/threads/'+str(thread_id)+'/turns',{'prompt_text':json.dumps(plan,ensure_ascii=False,allow_nan=False)}))
            return {'engine':'open-duet','mode':'PLAN_ONLY','state':'QUEUED','agent_id':agent_id,'thread_id':thread_id,'turn_id':turn_id,'answer_verified':False,'financial_action_authorized':False}
        except (httpx.HTTPError,ValueError,TypeError):raise EngineOutcomeUnknown('No authenticated planning acknowledgement; never auto-retry.') from None


def desktop_probe(config):
    """Only `status`, bounded output and timeout. No shell or desktop action tool."""
    binary=Path(config['binary'])
    if binary.is_symlink() or not binary.is_file() or binary.stat().st_size>64*1024*1024 or hashlib.sha256(binary.read_bytes()).hexdigest()!=config['sha256']:
        raise EngineUnavailable('Runtime changed before invocation.')
    output=bytearray();overflow=threading.Event()
    try:
        with subprocess.Popen([str(binary),'status'],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,shell=False) as process:
            def drain():
                while chunk:=process.stdout.read(1024):
                    if len(output)+len(chunk)>32768:
                        overflow.set();process.kill();return
                    output.extend(chunk)
            reader=threading.Thread(target=drain,daemon=True);reader.start()
            try:code=process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill();process.wait();raise EngineOutcomeUnknown('Local runtime timed out.') from None
            reader.join(timeout=1)
            if reader.is_alive() or overflow.is_set() or code!=0:raise EngineOutcomeUnknown('Local runtime response unavailable.')
        value=strict_json(output)
        return {'engine':'agent-desktop','mode':'STATUS_ONLY','state':'PROBED',
                'status_sha256':hashlib.sha256(output).hexdigest(),'runtime_response_received':True,
                'hardware_qualified':False,'desktop_action_executed':False,'financial_action_authorized':False}
    except (OSError,ValueError,TypeError,RecursionError):raise EngineOutcomeUnknown('Local runtime response not verified.') from None


def execute(policy,actor,company,engine,plan,transport=None):
    config=configuration(policy,actor,company,engine)
    return duet_plan(config,plan,transport) if engine=='open-duet' else desktop_probe(config)
