"""Disposable physical-room/ledger fixture; no production inventory seeding."""
def install(case,create):
    from django.utils import timezone
    from apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.hoteles.models import Room,RoomType
    from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.productos_servicios.models import Product,OperationalTag,PoliticaCancelacion
    from apps.core.catalogs.models import Amenity
    from apps.core_erp.accounting.models import Account
    from apps.core_erp.accounting.ledger_engine import LedgerEngine
    for model in (PoliticaCancelacion,OperationalTag,Amenity,Product,RoomType,Room):create(model)
    product=Product.objects.create(provider_id=case.provider.pk,nombre='Synthetic hotel room',tipo='SERVICIO',base_price='1.00')
    kind=RoomType.objects.create(provider_id=case.provider.pk,product=product,capacidad=2)
    rooms=[Room.objects.create(provider_id=case.provider.pk,room_type=kind,numero_habitacion=str(i+1)) for i in range(2)]
    expense=Account.plain_objects.create(tenant=case.tenant,chart_of_accounts=case.chart,code='HOTEL-FIX-COST',name='Synthetic hotel expense',type='EXPENSE')
    LedgerEngine.post_lines(tenant_id=case.tenant.pk,entry_date=timezone.localdate(),description='Synthetic hotel operating expense',lines_data=[{'account':expense,'debit':'2.00'},{'account':case.a,'credit':'2.00'}],actor=case.user,idempotency_key='hotel-operating-expense')
    return {'day':timezone.localdate().isoformat(),'room_ids':[str(r.pk) for r in rooms],'mapping':{'room_revenue':[str(case.b.pk)],'other_operating_revenue':[],'operating_expenses':[str(expense.pk)],'excluded_nonoperating':[]},'evidence_digest':'a'*64,'expected_revision':0,'confirmed':True}
