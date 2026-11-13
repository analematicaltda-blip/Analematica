from .publishing import Publishing
from .publishing_store import Store
def service(crm):return Publishing(Store(crm.store),crm)
