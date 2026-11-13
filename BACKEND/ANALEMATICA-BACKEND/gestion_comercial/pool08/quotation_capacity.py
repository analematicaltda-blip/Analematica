"""Read the owning provider's existing service/hold ledger; do not create holds."""
from datetime import datetime,timezone
from django.db import connection
from .crm import CRMError
from .opportunities import uuid_ref
class Capacity:
    def __init__(self,crm):self.crm=crm;self.provider=crm.store.provider
    def models(self):
        from apps.turismo.models import TourismService,Reservation,AvailabilityHold
        tables=set(connection.introspection.table_names())
        if any(m._meta.db_table not in tables for m in (TourismService,Reservation,AvailabilityHold)):raise CRMError('CAPACITY_SCHEMA_REQUIRED',503)
        return TourismService
    def resources(self):
        self.crm.authorize();model=self.models();rows=list(model.objects.filter(provider_id=self.provider,is_active=True).order_by('pk')[:101]);return {'resources':[{'id':str(x.pk),'name':x.name,'capacity':x.capacity,'source':'OWNED_TOURISM_SERVICE'} for x in rows[:100]],'truncated':len(rows)>100}
    def resource(self,ref):
        self.crm.authorize();uuid_ref(ref);row=self.models().objects.filter(pk=ref,provider_id=self.provider,is_active=True).first()
        if row is None:raise CRMError('RESOURCE_NOT_FOUND',404)
        return row
    def inspect(self,ref,start,end,quantity):
        from apps.prestadores.mi_negocio.gestion_comercial.availability import inspect
        row=self.resource(ref);data=inspect(row,start,end,quantity,datetime.now(timezone.utc));return {'resource_ref':ref,'source':'OWNED_SERVICE_RESERVATIONS_AND_HOLDS','available':data['can_hold'],'quantity':quantity,'remaining_units':data['remaining_units'],'requires_reconciliation':data['requires_reconciliation'],'checked_at':datetime.now(timezone.utc).isoformat(),'reserved':False}
