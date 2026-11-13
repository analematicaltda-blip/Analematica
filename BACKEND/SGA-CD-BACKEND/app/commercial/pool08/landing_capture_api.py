"""Transport helpers: same-origin HTML forms only; public responses never reveal CRM identity."""
import secrets,re,html
from urllib.parse import parse_qsl
from .crm import CRMError
from .landings import HEADERS,Landings,public_html
from .landing_store import Store as LandingStore
from .capture_store import Store as CaptureStore
from .landing_capture import Capture,UTM
COOKIE='landing_browser'
PUBLIC_HEADERS={**HEADERS,'Content-Security-Policy':HEADERS['Content-Security-Policy'].replace("form-action 'none'","form-action 'self'")}
def parse_form(raw,kind):
    if kind.split(';')[0].strip()!='application/x-www-form-urlencoded':raise CRMError('PUBLIC_FORM_CONTENT_TYPE',415)
    if len(raw)>12000:raise CRMError('PUBLIC_FORM_TOO_LARGE',413)
    try:
        pairs=parse_qsl(raw.decode('utf-8'),keep_blank_values=True,max_num_fields=12,errors='strict');data=dict(pairs)
        if len(data)!=len(pairs):raise ValueError()
        return data
    except (ValueError,UnicodeError):raise CRMError('INVALID_PUBLIC_FORM',400) from None

def service(crm):return Capture(CaptureStore(crm.store),crm,Landings(LandingStore(crm.store),crm),key())
def public_document(db,ref,path,origin,browser,query):
    # Validate the public snapshot before resolving any owner context.
    if not re.fullmatch('[a-f0-9]{32}',browser or ''):browser=''
    existing=public_html(LandingStore,db,ref);page=LandingStore.public(db,ref)[0]
    v=next(x for x in page['versions'] if x['number']==page['published_version'])
    canonical=path  # Resolve on the serving origin; never advertise the internal proxy host.
    if not v['content'].get('capture'):
        e=lambda v:html.escape(v,quote=True)
        return existing.replace('</head>','<link rel="canonical" href="'+e(canonical)+'"><meta property="og:title" content="'+e(v['content']['title'])+'"><meta property="og:description" content="'+e(v['content']['description'])+'"></head>'),browser
    crm=owner_crm(db,ref);capture=service(crm)
    if not re.fullmatch('[a-f0-9]{32}',browser or ''):browser=secrets.token_hex(16)
    for k in UTM:
        if len(query.getlist(k))>1:raise CRMError('DUPLICATE_ATTRIBUTION_FIELD',400)
    return capture.form(ref,browser,{k:query.get(k,'') for k in UTM},path.rstrip('/')+'/capture'+('/' if path.endswith('/') else ''),canonical),browser

def receipt_html(ref,result,path):
    e=lambda v:html.escape(v,quote=True)
    if result.get('withdrawn'):return '<!doctype html><html lang="es"><meta charset="utf-8"><body style="background:#071b34;color:white"><h1>Declaración retirada</h1><p>El reintento no reactiva la solicitud ni su consentimiento.</p></body></html>'
    return '<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Solicitud recibida</title><body style="background:#071b34;color:white;font:18px system-ui;padding:24px"><main><h1>Solicitud recibida</h1><p>No se verificó la titularidad del correo ni se enviaron mensajes. Conserva esta página para retirar tu declaración.</p><form method="post" action="'+e(path.rstrip('/').removesuffix('/capture')+'/withdraw'+('/' if path.endswith('/') else ''))+'"><input type="hidden" name="reference" value="'+e(result['reference'])+'"><input type="hidden" name="proof" value="'+e(result['withdrawal_proof'])+'"><button style="background:#0a243d;color:white;border:1px solid #75c9ff;padding:10px">Retirar mi declaración y solicitud</button></form></main></body></html>'

def same_origin(actual,expected):
    if actual!=expected:raise CRMError('PUBLIC_FORM_ORIGIN_REJECTED',403)

def key():
    from app.core.config import settings
    return settings.SECRET_KEY.encode()
def owner_crm(db,ref):
    from types import SimpleNamespace
    from starlette.datastructures import QueryParams
    from app.models.user import Usuario
    from .crm_api import service as make_crm
    doc=LandingStore.public(db,ref)[0];scope=LandingStore.public_scope(db,ref)
    if not str(doc.get('publisher_ref','')).isdigit():raise CRMError('PUBLIC_FORM_OWNER_UNAVAILABLE',403)
    user=db.get(Usuario,int(doc['publisher_ref']))
    if not user or not user.activo:raise CRMError('PUBLIC_FORM_OWNER_UNAVAILABLE',403)
    crm=make_crm(SimpleNamespace(method='POST',query_params=QueryParams()),db,user)
    if crm.store.scope!=scope['scope']:raise CRMError('PUBLIC_FORM_SCOPE_UNAVAILABLE',403)
    return crm

def error_html(code):
    messages={'PUBLIC_FORM_RATE_LIMIT':'Recibimos demasiadas solicitudes en este momento. Intenta de nuevo más tarde.','FORM_PROOF_INVALID_OR_EXPIRED':'El formulario venció o no pudo validarse. Abre de nuevo la página antes de enviar.','FORM_PAGE_CHANGED_OR_WITHDRAWN':'La página cambió o fue retirada. Revisa su versión vigente.','FORM_DISABLED':'Este formulario no está disponible.','LANDING_NOT_FOUND':'La página no está publicada o no existe.'}
    message=messages.get(code,'No pudimos confirmar la solicitud. Revisa los datos y vuelve a la página de la empresa. No se enviaron mensajes.')
    return '<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Solicitud no confirmada</title><body style="background:#071b34;color:white;font:18px system-ui;padding:24px"><h1>Solicitud no confirmada</h1><p>'+html.escape(message)+'</p></body></html>'
