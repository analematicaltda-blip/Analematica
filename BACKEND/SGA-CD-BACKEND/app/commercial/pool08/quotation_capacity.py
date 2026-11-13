"""Read SGA's own scoped spaces/bookings; never reserve a space from a quote."""
from datetime import datetime,timezone
from sqlalchemy import inspect,or_
from .crm import CRMError
class Capacity:
    def __init__(self,crm):self.crm=crm;self.db=crm.store.db;self.tenant=crm.store.tenant
    def resources(self):
        self.crm.authorize()
        from app.models.academic import EscenarioParte,Escenario
        tables=inspect(self.db.get_bind()).get_table_names()
        if any(x.__tablename__ not in tables for x in (EscenarioParte,Escenario)):raise CRMError('CAPACITY_SCHEMA_REQUIRED',503)
        rows=self.db.query(EscenarioParte).join(Escenario).filter(EscenarioParte.inquilino_id==self.tenant,Escenario.inquilino_id==self.tenant).order_by(EscenarioParte.id).limit(101).all()
        return {'resources':[{'id':str(x.id),'name':x.nombre_parte,'capacity':x.capacidad,'source':'SGA_OWNED_SPACE_PART'} for x in rows[:100]],'truncated':len(rows)>100}
    def resource(self,ref):
        self.crm.authorize()
        from app.models.academic import EscenarioParte,Escenario
        if not isinstance(ref,str) or len(ref)>19 or not ref.isascii() or not ref.isdecimal() or not 0<int(ref)<2**63:raise CRMError('INVALID_RESOURCE')
        self.resources()
        row=self.db.query(EscenarioParte).join(Escenario).filter(EscenarioParte.id==int(ref),EscenarioParte.inquilino_id==self.tenant,Escenario.inquilino_id==self.tenant).first()
        if row is None:raise CRMError('RESOURCE_NOT_FOUND',404)
        return row
    def inspect(self,ref,start,end,quantity):
        from app.models.academic import Reserva,Clase
        row=self.resource(ref);tables=inspect(self.db.get_bind()).get_table_names()
        if any(x.__tablename__ not in tables for x in (Reserva,Clase)):raise CRMError('CAPACITY_SCHEMA_REQUIRED',503)
        from .sales_models import SaleSpaceClaim
        ignored=[]
        if SaleSpaceClaim.__tablename__ in tables:ignored=[row[0] for row in self.db.query(SaleSpaceClaim.reservation_id).join(Reserva,Reserva.id==SaleSpaceClaim.reservation_id).filter(SaleSpaceClaim.scope==self.crm.store.scope,SaleSpaceClaim.released==True,Reserva.estado=='Cancelada',Reserva.proposito==('Venta '+SaleSpaceClaim.sale_id)).all()]
        booked=self.db.query(Reserva.id).filter(~Reserva.id.in_(ignored)).filter(Reserva.escenario_parte_id==row.id,Reserva.fecha_inicio<end,Reserva.fecha_fin>start).first() is not None
        classes=self.db.query(Clase.id).filter(Clase.escenario_id==row.escenario_id,or_(Clase.fecha==None,(Clase.fecha>=start.replace(hour=0,minute=0,second=0,microsecond=0))&(Clase.fecha<=end.replace(hour=23,minute=59,second=59)))).first() is not None
        capacity=row.capacidad if type(row.capacidad)==int and row.capacidad>0 else 0
        return {'resource_ref':ref,'source':'SGA_OWNED_SPACE_AND_BOOKINGS','available':bool(capacity>=quantity and not booked and not classes),'quantity':quantity,'remaining_units':0 if booked or classes else capacity,'requires_reconciliation':classes,'checked_at':datetime.now(timezone.utc).isoformat(),'reserved':False,'semantics':'EXCLUSIVE_SPACE_CONSERVATIVE_CLASSES'}
