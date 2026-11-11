"""Owner + live ERP session + reviewed binding. GET-only shared-ledger bridge."""
import os,re,json
from datetime import datetime,timezone,timedelta,date
from uuid import UUID
from urllib.parse import urlsplit
import httpx
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.models.corporate import CorporateLedgerBinding,CorporateOwner
from app.models.user import Usuario
from app.services.corporate_policy import require_owner
from app.services.workspace_service import roles_of

COOKIE='sgacd_erp_tur_session'
BASE='/api/v1/mi-negocio/contable/contabilidad/cuentas/'
MAX_RESPONSE=1024*1024

def utc(value):return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)

def review_binding(db,*,operator,owner_id,ledger_actor_id,provider_id,tenant_id,evidence_digest,valid_until,apply=False):
    operator=db.get(Usuario,getattr(operator,'id',None),populate_existing=True) if getattr(operator,'id',None) is not None else None
    if operator is not None:db.expire(operator,['roles'])
    if operator is None or not operator.activo or 'admin_general' not in roles_of(operator) or operator.id==owner_id:raise HTTPException(403,'Se requiere revisión independiente autorizada.')
    owner=db.get(Usuario,owner_id,populate_existing=True);binding=db.get(CorporateOwner,1,populate_existing=True)
    if not owner or not owner.activo or not binding or binding.user_id!=owner_id:raise HTTPException(403,'Titular corporativo no vigente.')
    now=datetime.now(timezone.utc)
    if not isinstance(valid_until,datetime) or valid_until.tzinfo is None or not now<valid_until<=now+timedelta(days=30):raise HTTPException(422,'Vigencia máxima de treinta días.')
    if not isinstance(evidence_digest,str) or not re.fullmatch('[0-9a-f]{64}',evidence_digest):raise HTTPException(422,'Huella de revisión requerida.')
    if not isinstance(ledger_actor_id,str) or not re.fullmatch('[1-9][0-9]{0,18}',ledger_actor_id):raise HTTPException(422,'Actor contable inválido.')
    try:provider=str(UUID(str(provider_id)));tenant=str(UUID(str(tenant_id)))
    except ValueError:raise HTTPException(422,'Identificadores contables inválidos.') from None
    if db.get(CorporateLedgerBinding,1):raise HTTPException(409,'El vínculo existente requiere recuperación revisada, sin sobrescritura.')
    row=CorporateLedgerBinding(id=1,owner_id=owner_id,reviewer_id=operator.id,ledger_actor_id=ledger_actor_id,provider_id=provider,tenant_id=tenant,evidence_digest=evidence_digest,valid_until=valid_until)
    if apply:db.add(row);db.commit();db.refresh(row)
    return row

def require_binding(db,user):
    user=db.get(Usuario,getattr(user,'id',None),populate_existing=True)
    if user is None:raise HTTPException(403,'Titular corporativo no vigente.')
    db.expire(user,['roles'])
    db.get(CorporateOwner,1,populate_existing=True)
    require_owner(db,user)
    try:row=db.get(CorporateLedgerBinding,1)
    except SQLAlchemyError:raise HTTPException(503,'Falta preparar el esquema del vínculo contable.') from None
    if row is None:raise HTTPException(503,'Falta vincular y revisar la empresa contable de Analemática.')
    db.refresh(row)
    reviewer=db.get(Usuario,row.reviewer_id,populate_existing=True)
    if reviewer is not None:db.expire(reviewer,['roles'])
    if row.owner_id!=user.id or row.reviewer_id==user.id or not re.fullmatch('[0-9a-f]{64}',row.evidence_digest) or row.revoked_at or utc(row.valid_until)<=datetime.now(timezone.utc) or not reviewer or not reviewer.activo or 'admin_general' not in roles_of(reviewer):
        raise HTTPException(403,'El vínculo contable no está vigente.')
    return row

def verify_dispatch_result(recheck,db,user,selected):
    """Suppress stale-authority responses without claiming distributed rollback."""
    try:recheck(db,user,selected)
    except HTTPException as exc:
        raise HTTPException(exc.status_code,'El acceso cambió durante la operación; el resultado puede estar registrado. No crees otra solicitud: recupera la revisión con acceso autorizado.') from None


def origin():
    value=os.environ.get('CORPORATE_LEDGER_ORIGIN','')
    if any(ord(c)<33 for c in value):raise HTTPException(503,'Origen contable inválido.')
    try:
        parsed=urlsplit(value);port=parsed.port
    except ValueError:raise HTTPException(503,'Origen contable inválido.') from None
    if parsed.username or parsed.password or parsed.path not in ('','/') or parsed.query or parsed.fragment or not parsed.hostname:
        raise HTTPException(503,'Origen del ledger no configurado de forma segura.')
    if parsed.scheme!='https' and not(parsed.scheme=='http' and parsed.hostname in {'127.0.0.1','localhost','::1'}):
        raise HTTPException(503,'El ledger requiere HTTPS o loopback local.')
    return value.rstrip('/')

def client():return httpx.Client(timeout=httpx.Timeout(8,connect=3),follow_redirects=False,trust_env=False)

def reject_upstream_throttle(response):
    if response.status_code==429:
        raw=response.headers.get('Retry-After','')
        seconds=min(3600,max(1,int(raw))) if isinstance(raw,str) and re.fullmatch('[0-9]{1,5}',raw) else 60
        raise HTTPException(429,'Límite temporal del ERP. Espera y consulta el estado de la misma operación antes de reintentar.',headers={'Retry-After':str(seconds)})

def fetch(client,url,cookie,params):
    with client.stream('GET',url,headers={'Cookie':COOKIE+'='+cookie,'Accept':'application/json','Accept-Encoding':'identity'},params=params) as response:
        reject_upstream_throttle(response)
        if response.status_code in (401,403):raise HTTPException(403,'Inicia sesión con el titular autorizado en el acceso seguro del ERP.')
        if response.status_code!=200:raise HTTPException(503,'El libro mayor no está disponible para esta consulta.')
        if response.headers.get('content-encoding','identity').lower()!='identity':raise HTTPException(503,'Codificación de reporte no admitida.')
        chunks=[];size=0
        for chunk in response.iter_bytes(chunk_size=65536):
            size+=len(chunk)
            if size>MAX_RESPONSE:raise HTTPException(503,'El reporte supera el tamaño admitido.')
            chunks.append(chunk)
    try:raw=json.loads(b''.join(chunks));return raw['data'] if isinstance(raw,dict) and raw.get('success') is True else raw
    except (ValueError,KeyError):raise HTTPException(503,'Respuesta contable incompatible.') from None

def read_report(db,*,user,session_cookie,report,since=None,until=None,account_id=None):
    link=require_binding(db,user)
    if not isinstance(session_cookie,str) or not re.fullmatch('[a-z0-9]{32}',session_cookie):raise HTTPException(403,'Abre primero una sesión del ERP con el titular contable verificado.')
    if report not in {'trial_balance','profitability','tax_reconciliation','tax_register','quick_ratio'}:raise HTTPException(422,'Reporte no soportado.')
    try:
        end=date.fromisoformat(until) if isinstance(until,str) and len(until)==10 else None
        if end is None or end.isoformat()!=until:raise ValueError()
        if report in {'profitability','tax_reconciliation','tax_register'}:
            start=date.fromisoformat(since) if isinstance(since,str) and len(since)==10 else None
            if start is None or start.isoformat()!=since or start>end or (end-start).days>366:raise ValueError()
        elif since is not None:raise ValueError()
    except ValueError:raise HTTPException(422,'Intervalo contable inválido.') from None
    if report in {'tax_reconciliation','tax_register'}:
        try:account_id=str(UUID(str(account_id)))
        except ValueError:raise HTTPException(422,'Selecciona una cuenta tributaria revisada.') from None
    elif account_id is not None:raise HTTPException(422,'Cuenta no admitida para este reporte.')
    selected={k:getattr(link,k) for k in ['owner_id','reviewer_id','ledger_actor_id','provider_id','tenant_id','evidence_digest','valid_until']}
    params={'provider_id':link.provider_id};target=origin()
    try:
        with client() as transport:
            combined=os.environ.get('CORPORATE_LEDGER_COMBINED_CONTEXT_ENABLED')=='1'
            if not combined:
                identity=fetch(transport,target+BASE+'identidad-contable/',session_cookie,params)
                if not isinstance(identity,dict) or identity.get('company_id')!=link.tenant_id or identity.get('provider_id')!=link.provider_id or str(identity.get('actor_id'))!=link.ledger_actor_id:
                    raise HTTPException(403,'Las identidades corporativa y contable no coinciden con el vínculo revisado.')
            path={'quick_ratio':'liquidez-acida/','trial_balance':'balance-prueba/','profitability':'rentabilidad/','tax_reconciliation':'conciliacion-tributaria/','tax_register':'conciliacion-tributaria-integral/'}[report]
            query={**params,**({'fecha_corte':until} if report in {'trial_balance','quick_ratio'} else {'desde':since,'hasta':until})}
            if report in {'tax_reconciliation','tax_register'}:query['cuenta_id']=account_id
            if combined:
                wrapped=fetch(transport,target+BASE+'lectura-contable/',session_cookie,{**query,'report':report})
                if not isinstance(wrapped,dict) or set(wrapped)!={'schema','report','context','data'} or wrapped.get('schema')!='sgacd-accounting-read-context-v1' or wrapped.get('report')!=report:raise HTTPException(503,'Reporte agregado incompatible.')
                context=wrapped['context']
                if not isinstance(context,dict) or set(context)!={'company_id','provider_id','actor_id','read_only'} or context['read_only'] is not True or context['company_id']!=link.tenant_id or context['provider_id']!=link.provider_id or str(context['actor_id'])!=link.ledger_actor_id:raise HTTPException(403,'Identidad del reporte no vigente.')
                data=wrapped['data']
            else:data=fetch(transport,target+BASE+path,session_cookie,query)
    except (httpx.HTTPError,httpx.InvalidURL):raise HTTPException(503,'No se pudo consultar el ledger; no se modificó información.') from None
    # Independent read transaction: do not reuse the initial identity-map/snapshot.
    with Session(bind=db.get_bind(),autoflush=False) as final_db:
        fresh=final_db.get(Usuario,user.id)
        if fresh is None:raise HTTPException(403,'La identidad corporativa dejó de estar vigente.')
        current=require_binding(final_db,fresh)
        if any(getattr(current,k)!=v for k,v in selected.items()):raise HTTPException(403,'El vínculo cambió durante la consulta.')
        current_tenant=current.tenant_id
    if not isinstance(data,dict) or data.get('tenant_id')!=current_tenant:raise HTTPException(503,'El reporte pertenece a un contexto incompatible.')
    if data.get('posted_only') is not True or data.get('valuation')!='base_currency':raise HTTPException(503,'Reporte sin alcance contable verificable.')
    money=lambda v:isinstance(v,str) and re.fullmatch(r'-?[0-9]{1,26}\.[0-9]{2}',v)
    if report=='quick_ratio':
        from app.services.quick_ratio_contract import validate
        try:validate(data,company_id=current_tenant,cutoff=until)
        except (ValueError,TypeError,KeyError):raise HTTPException(503,'Indicador de liquidez incompatible.') from None
    elif report=='trial_balance':
        if data.get('cutoff_date')!=until or not all(money(data.get(k)) for k in ['total_debit','total_credit']) or not isinstance(data.get('lines'),list):raise HTTPException(503,'Balance incompatible.')
    elif report=='tax_register':
        from app.services.tax_register_contract import validate
        try:validate(data,company_id=current_tenant,account_id=account_id,since=since,until=until)
        except (ValueError,TypeError,KeyError):raise HTTPException(503,'Registro tributario integral incompatible.') from None
    elif report=='tax_reconciliation':
        if data.get('account_id')!=account_id or data.get('since')!=since or data.get('until')!=until or not all(money(data.get(k)) for k in ['debit','credit','net_liability_movement','reviewed_reservation_tax','unattributed_net']) or data.get('dian_compared') is not False or not isinstance(data.get('lines'),list):raise HTTPException(503,'Conciliación tributaria incompatible.')
    elif data.get('start_date')!=since or data.get('end_date')!=until or not all(money(data.get(k)) for k in ['revenue','expenses','net_profit']):raise HTTPException(503,'Resultado incompatible.')
    return {'schema':'sgacd-corporate-ledger-v1','report':report,'company_id':current_tenant,'source':'authenticated_shared_ledger',
        'read_only':True,'ledger_written':False,'data':data,'fiscal_acceptance':'NOT_VERIFIED'}
