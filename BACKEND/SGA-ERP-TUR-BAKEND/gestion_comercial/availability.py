"""Scoped, unpriced capacity holds; never confirms a reservation or payment."""
import hashlib,json
from uuid import UUID
from datetime import datetime,timedelta,timezone as utc_timezone
from django.db import transaction,IntegrityError
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import APIException,ValidationError,NotFound
from apps.turismo.models import TourismService,Reservation,AvailabilityHold
from apps.turismo.services.company_identity import resolve_company

class CapacityConflict(APIException):
    status_code=409
    default_detail='No hay cupos suficientes o el intervalo requiere conciliación.'


def parse(data,creating=False):
    fields={'provider_id','service_id','start_at','end_at','quantity'}
    if creating:fields.add('idempotency_key')
    if not isinstance(data,dict) or set(data)!=fields:raise ValidationError('Se requiere prestador, servicio, intervalo y cantidad; solo la creación requiere idempotency_key.')
    value={}
    for field in ('provider_id','service_id')+ (('idempotency_key',) if creating else ()):
        try:value[field]=UUID(str(data[field]))
        except (TypeError,ValueError,AttributeError):raise ValidationError('Identificador inválido.')
    for field in ('start_at','end_at'):
        text=data[field]
        if not isinstance(text,str) or len(text)>64:raise ValidationError('Fecha inválida.')
        try:
            if datetime.fromisoformat(text.replace('Z','+00:00')).tzinfo is None:raise ValueError()
        except ValueError:raise ValidationError('La fecha debe incluir zona horaria explícita.')
        value[field]=serializers.DateTimeField().run_validation(text)
    quantity=data['quantity']
    if type(quantity) is not int or not 1<=quantity<=10000:raise ValidationError('La cantidad debe ser un entero entre1 y10000.')
    value['quantity']=quantity
    if value['end_at']<=value['start_at'] or value['end_at']-value['start_at']>timedelta(days=365):raise ValidationError('El intervalo debe ser positivo y no superar365 días.')
    return value


def authorize(user,value,lock=False):
    resolve_company(user,value['provider_id'])
    query=TourismService.objects
    if lock:query=query.select_for_update()
    service=query.filter(pk=value['service_id'],provider_id=value['provider_id']).first()
    if service is None:raise NotFound('Servicio no disponible para este prestador.')
    return service


def inspect(service,start,end,quantity,now):
    legacy=Reservation.objects.filter(service=service,is_active=True,status__in=['PENDING','CONFIRMED','COMPLETED'],start_date__lt=end,end_date__gt=start).exists()
    query=AvailabilityHold.objects.filter(service=service,released_at__isnull=True,expires_at__gt=now,start_at__lt=end,end_at__gt=start)
    holds=list(query.values_list('start_at','end_at','quantity')[:10001])
    events=[]
    for first,last,units in holds:
        events.extend([(max(first,start),units),(min(last,end),-units)])
    current=peak=0
    for _,delta in sorted(events,key=lambda item:(item[0],item[1])):
        current+=delta;peak=max(peak,current)
    uncertain=legacy or len(holds)>10000
    enabled=service.is_active and service.availability and service.capacity>0
    remaining=None if uncertain else max(0,service.capacity-peak) if enabled else 0
    return {'service_id':str(service.pk),'capacity_units':service.capacity,'remaining_units':remaining,'can_hold':bool(enabled and not uncertain and quantity<=remaining),'requires_reconciliation':uncertain,'interval_semantics':'HALF_OPEN_SERVICE_UNITS','price_state':'UNPRICED_NO_PAYMENT'}


def availability(user,data):
    value=parse(data);service=authorize(user,value);now=timezone.now()
    if value['start_at']<now:raise ValidationError('El intervalo debe comenzar en el futuro.')
    return inspect(service,value['start_at'],value['end_at'],value['quantity'],now)


def present(hold):
    now=timezone.now()
    return {'id':str(hold.pk),'provider_id':str(hold.provider_id),'service_id':str(hold.service_id),'start_at':hold.start_at,'end_at':hold.end_at,'quantity':hold.quantity,'expires_at':hold.expires_at,'status':'RELEASED' if hold.released_at else 'EXPIRED' if hold.expires_at<=now else 'HELD','price_state':'UNPRICED_NO_PAYMENT','reservation_confirmed':False}


@transaction.atomic
def create_hold(user,data):
    value=parse(data,creating=True);service=authorize(user,value,lock=True)
    body={key:item.astimezone(utc_timezone.utc).isoformat() if key in {'start_at','end_at'} else str(item) if isinstance(item,UUID) else item for key,item in value.items() if key!='idempotency_key'}
    digest=hashlib.sha256(json.dumps(body,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    old=AvailabilityHold.objects.filter(provider=service.provider_id,requested_by=user,idempotency_key=value['idempotency_key']).first()
    if old:
        if old.request_digest!=digest:raise CapacityConflict('La clave de idempotencia ya tiene otro contenido.')
        return old,False
    now=timezone.now()
    if value['start_at']<now:raise ValidationError('El intervalo debe comenzar en el futuro.')
    if not inspect(service,value['start_at'],value['end_at'],value['quantity'],now)['can_hold']:raise CapacityConflict()
    try:
        with transaction.atomic():hold=AvailabilityHold.objects.create(provider_id=service.provider_id,service=service,requested_by=user,idempotency_key=value['idempotency_key'],request_digest=digest,start_at=value['start_at'],end_at=value['end_at'],quantity=value['quantity'],expires_at=now+timedelta(minutes=10))
    except IntegrityError:
        old=AvailabilityHold.objects.filter(provider_id=service.provider_id,requested_by=user,idempotency_key=value['idempotency_key']).first()
        if old and old.request_digest==digest:return old,False
        raise CapacityConflict('La clave de idempotencia ya fue utilizada.')
    return hold,True


@transaction.atomic
def release_hold(user,pk):
    candidate=AvailabilityHold.objects.filter(pk=pk,requested_by=user).first()
    if candidate is None:raise NotFound('Retención no disponible.')
    resolve_company(user,candidate.provider_id)
    TourismService.objects.select_for_update().get(pk=candidate.service_id)
    hold=AvailabilityHold.objects.select_for_update().get(pk=candidate.pk)
    from apps.core_erp.accounting.commercial_sales_guard import require_hold_release
    require_hold_release(hold)
    if hold.released_at is None:
        hold.released_at=timezone.now();hold.save(update_fields=['released_at'])
    return hold
