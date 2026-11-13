from .ads import Ads
from .ads_store import Store
def service(crm):return Ads(Store(crm.store),crm)
