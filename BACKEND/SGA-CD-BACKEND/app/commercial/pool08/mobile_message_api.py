from .mobile_messages import MobileMessages
from .mobile_message_store import Store
HEADERS={'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer'}
def service(crm):return MobileMessages(Store(crm.store),crm)
def receiver(db,ref):return MobileMessages(Store.public(db,ref))
