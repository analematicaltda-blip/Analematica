from .generation import Generation
from .generation_store import Store
HEADERS={'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Content-Security-Policy':"default-src 'none'; frame-ancestors 'none'",'Referrer-Policy':'no-referrer','Content-Disposition':'attachment; filename="generation-result.bin"'}
def service(crm):return Generation(Store(crm.store),crm)
