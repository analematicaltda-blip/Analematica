"""Two-process capacity/idempotency contracts within the isolated PostgreSQL fixture."""
import uuid
_BARRIER=None

def attempt(payload):
    from django.db import connections
    from django.contrib.auth import get_user_model
    from rest_framework.exceptions import APIException
    from apps.prestadores.mi_negocio.gestion_comercial.availability import create_hold
    try:
        connections.close_all();_BARRIER.wait(timeout=10)
        user=get_user_model().objects.get(pk=payload['actor'])
        try:
            hold,created=create_hold(user,payload['body'])
            return {'accepted':True,'id':str(hold.pk),'created':created}
        except APIException as error:return {'accepted':False,'status':error.status_code}
    finally:connections.close_all()


def run(context,create):
    from datetime import timedelta
    from concurrent.futures import ProcessPoolExecutor
    from django.db import connections
    from django.utils import timezone
    from api.models import CustomUser
    from apps.core_erp.tenancy.models import Tenant
    from apps.turismo.models import TourismProvider,BusinessProfile,TourismService,Reservation,VerifiedCompanyLink,AvailabilityHold
    for model in (Tenant,TourismProvider,BusinessProfile,TourismService,Reservation,VerifiedCompanyLink,AvailabilityHold):create(model)
    global _BARRIER
    results=[]
    for mode in ('last_unit','idempotent_retry','key_conflict_across_services'):
        user=CustomUser(username='capacity-'+uuid.uuid4().hex,is_active=True);reviewer=CustomUser(username='reviewer-'+uuid.uuid4().hex,is_active=True,is_superuser=True);CustomUser.objects.bulk_create([user,reviewer])
        provider=TourismProvider.objects.create(owner=user,name='Synthetic capacity',provider_type='GUIDE')
        tax=uuid.uuid4().hex
        BusinessProfile.objects.create(provider=provider,legal_name='test',tax_id=tax,business_address='test',phone='test',email='test@example.test')
        tenant=Tenant.objects.create(name='Synthetic tenant',tax_id=tax,state='ACTIVE')
        VerifiedCompanyLink.objects.create(provider=provider,tenant=tenant,administrator=user,reviewed_by=reviewer,verified_tax_id=tax,evidence_digest='a'*64,verified_at=timezone.now(),valid_until=timezone.now()+timedelta(days=1))
        service=TourismService.objects.create(provider=provider,name='Synthetic unit',description='test',service_type='TOUR',price='1.00',capacity=1)
        start=timezone.now()+timedelta(days=1)
        body={'provider_id':str(provider.pk),'service_id':str(service.pk),'start_at':start.isoformat(),'end_at':(start+timedelta(hours=1)).isoformat(),'quantity':1,'idempotency_key':str(uuid.uuid4())}
        other=dict(body)
        if mode=='last_unit':other['idempotency_key']=str(uuid.uuid4())
        if mode=='key_conflict_across_services':
            second=TourismService.objects.create(provider=provider,name='Other unit',description='test',service_type='TOUR',price='1',capacity=1);other['service_id']=str(second.pk)
        _BARRIER=context.Barrier(2);connections.close_all()
        with ProcessPoolExecutor(max_workers=2,mp_context=context) as pool:
            futures=[pool.submit(attempt,{'actor':user.pk,'body':value}) for value in (body,other)]
            outcomes=[future.result(timeout=20) for future in futures]
        accepted=[value for value in outcomes if value['accepted']]
        assert len(accepted)==(2 if mode=='idempotent_retry' else 1),outcomes
        assert AvailabilityHold.objects.filter(provider=provider).count()==1
        if mode=='idempotent_retry':assert len({value['id'] for value in accepted})==1 and sum(value['created'] for value in accepted)==1
        else:assert [value['status'] for value in outcomes if not value['accepted']]==[409]
        results.append({'scenario':mode,'accepted':len(accepted),'persisted_holds':1,'overbooked':False})
    return results
