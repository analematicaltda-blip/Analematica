"""Private campaign services and narrowly scoped, signed public suppression."""
from .email_campaigns import EmailCampaigns
def receipt_service(db,ref):
 e=EmailCampaigns(Store.public(db,ref));e.actor="SIGNED_RECEIPT_ADAPTER";return e
from .email_campaign_store import Store
HEADERS={'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer','Content-Security-Policy':"default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'"}
def service(crm):return EmailCampaigns(Store(crm.store),crm)
def public(db,ref):return EmailCampaigns(Store.public(db,ref))
def form(engine,ref,contact,proof):
 import hmac
 from .crm import CRMError
 d=engine.raw(ref);r=next((r for r in d.get('recipients',[]) if r['contact_id']==contact),None)
 if not r or not hmac.compare_digest(engine.proof(d,r),proof):raise CRMError('EMAIL_UNSUBSCRIBE_NOT_FOUND',404)
 return '<!doctype html><html lang="es"><meta charset="utf-8"><body style="background:#11304b;color:white"><h1>Cancelar comunicaciones</h1><p>Confirmar bloqueará los correos pendientes. No cancela mensajes ya despachados.</p><form method="post"><input type="hidden" name="confirm" value="yes"><button>Cancelar comunicaciones comerciales</button></form></body></html>'
