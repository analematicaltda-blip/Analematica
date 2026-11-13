"""Django storage owned by the importing backend's own application label."""
from contextlib import contextmanager
from django.db import transaction,connection,IntegrityError,OperationalError
from . import identity_models as models
from .access_protocol import AccessFault
MODELS={'grant':models.CommercialGrant,'consent':models.CommercialConsent,'alias':models.CommercialIdentityAlias,'event':models.CommercialPolicyEvent}
class Store:
    def exists(self,kind):return MODELS[kind]._meta.db_table in connection.introspection.table_names()
    def ready(self):return all(self.exists(kind) for kind in MODELS)
    def get(self,kind,tenant,**filters):
        if not self.exists(kind):return None
        return MODELS[kind].objects.filter(tenant_ref=tenant,**filters).values().first()
    def get_by_id(self,kind,key):return MODELS[kind].objects.filter(pk=key).values().first()
    def list(self,kind,tenant,limit):return list(MODELS[kind].objects.filter(tenant_ref=tenant).order_by('-created_at','id').values()[:limit])
    def save(self,kind,row,expected):
        model=MODELS[kind]
        if expected==0:model.objects.create(**row)
        elif model.objects.filter(pk=row['id'],tenant_ref=row['tenant_ref'],revision=expected).update(**row)!=1:raise AccessFault('REVISION_CONFLICT',409)
    @contextmanager
    def transaction(self):
        try:
            with transaction.atomic():yield
        except (IntegrityError,OperationalError):raise AccessFault('ACCESS_WRITE_CONFLICT',409) from None
