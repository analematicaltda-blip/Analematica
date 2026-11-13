from .analytics import Analytics
from .analytics_store import Store
def service(crm):return Analytics(Store(crm.store),crm)
