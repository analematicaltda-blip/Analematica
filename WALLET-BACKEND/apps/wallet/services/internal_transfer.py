"""Same-ledger transfers, with two separate approvals by the requesting administrator."""
import hashlib
import hmac
import json
import secrets
from datetime import timedelta
from decimal import Decimal,InvalidOperation
from django.conf import settings
from django.db import transaction,models
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import APIException,PermissionDenied,ValidationError
from ..models import Wallet,WalletTransaccion,WalletMovimiento,WalletTransferIntent,WalletLimiteOperativo
from .wallet_service import WalletOperationUnavailable
from .access_policy import registered_actor,require_wallet_access,accessible_wallets


class TransferConflict(APIException):
    status_code=409
    default_code='wallet_transfer_conflict'
    default_detail='El estado del monedero o de la autorización cambió.'


def principal(user):
    registered_actor(user)
    if getattr(user,'is_agent',False):raise PermissionDenied('Las autorizaciones financieras requieren al titular personal.')
    if not getattr(settings,'WALLET_INTERNAL_TRANSFERS_ENABLED',False):
        raise WalletOperationUnavailable()


def money(value):
    try:
        amount=Decimal(str(value))
        if not amount.is_finite() or amount<=0 or amount>Decimal('9999999999999999.99') or amount!=amount.quantize(Decimal('0.01')):
            raise ValueError()
        return amount.quantize(Decimal('0.01'))
    except (InvalidOperation,ValueError,TypeError):
        raise ValidationError({'amount':'Importe positivo, finito y con máximo dos decimales requerido.'})


def fingerprint(source,destination,amount,currency,purpose=None):
    data={'source':str(source),'destination':str(destination),'amount':str(amount),'currency':currency}
    if purpose:data['purpose']=purpose
    return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def check_wallets(user,source,destination,amount):
    require_wallet_access(user,source)
    if source.pk==destination.pk:raise ValidationError('Origen y destino deben ser distintos.')
    if source.estado!=Wallet.Status.ACTIVO or destination.estado!=Wallet.Status.ACTIVO:raise TransferConflict('Ambos monederos deben estar activos.')
    if source.currency not in {'COP','USD','EUR'} or source.currency!=destination.currency:raise TransferConflict('Moneda no clasificada o monedas diferentes; no se realiza conversión.')
    if source.saldo_disponible<amount:raise TransferConflict('Saldo insuficiente.')
    if destination.saldo_disponible+amount>Decimal('9999999999999999.99'):raise TransferConflict('El saldo de destino supera la capacidad monetaria.')
    if any(value<0 for value in [source.saldo_disponible,source.saldo_bloqueado,source.saldo_en_proceso,destination.saldo_disponible,destination.saldo_bloqueado,destination.saldo_en_proceso]):raise TransferConflict('Los saldos requieren auditoría antes de operar.')
    limits=WalletLimiteOperativo.objects.filter(wallet=source).first()
    if limits is None:raise TransferConflict('Configure límites explícitos antes de transferir.')
    if limits.requiere_aprobacion_soberana:raise TransferConflict('Se requiere la autorización adicional de gobierno financiero; este flujo no la sustituye.')
    if limits.monto_maximo_transaccion<=0 or amount>limits.monto_maximo_transaccion:raise TransferConflict('Límite por operación excedido.')
    used=WalletTransferIntent.objects.filter(source=source,state='EXECUTED',executed_at__date=timezone.localdate()).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
    if limits.monto_maximo_diario<=0 or used+amount>limits.monto_maximo_diario:raise TransferConflict('Límite diario excedido.')


@transaction.atomic
def prepare(user,source_id,destination_id,amount,key):
    principal(user);amount=money(amount)
    source=get_object_or_404(accessible_wallets(user),pk=source_id)
    destination=get_object_or_404(Wallet,pk=destination_id)
    digest=fingerprint(source.pk,destination.pk,amount,source.currency)
    existing=WalletTransferIntent.objects.filter(requested_by_id=user.pk,idempotency_key=key).first()
    if existing:
        if existing.digest!=digest:raise TransferConflict('Clave de idempotencia reutilizada con otro contenido.')
        return existing
    check_wallets(user,source,destination,amount)
    intent,created=WalletTransferIntent.objects.get_or_create(requested_by_id=user.pk,idempotency_key=key,defaults={'source':source,'destination':destination,'amount':amount,'currency':source.currency,'digest':digest,'expires_at':timezone.now()+timedelta(minutes=15)})
    if intent.digest!=digest:raise TransferConflict('Clave de idempotencia reutilizada con otro contenido.')
    return intent


def owned_intent(user,intent_id,digest):
    principal(user)
    intent=get_object_or_404(WalletTransferIntent.objects.select_for_update(),pk=intent_id,requested_by_id=user.pk)
    require_wallet_access(user,intent.source)
    expected=fingerprint(intent.source_id,intent.destination_id,intent.amount,intent.currency,intent.purpose)
    if not hmac.compare_digest(str(digest),intent.digest) or not hmac.compare_digest(expected,intent.digest):raise TransferConflict('El resumen autorizado no coincide.')
    return intent


@transaction.atomic
def review(user,intent_id,digest,device_proof=None):
    intent=owned_intent(user,intent_id,digest)
    if intent.state!='PENDING' or intent.expires_at<=timezone.now():raise TransferConflict('La primera autorización ya fue usada o venció.')
    device=None
    if getattr(settings,'WALLET_DEVICE_APPROVALS_REQUIRED',True):
        from .device_approvals import consume
        device=consume(user,intent,'REVIEW',device_proof)
    token=secrets.token_urlsafe(32)
    changed=WalletTransferIntent.objects.filter(pk=intent.pk,state='PENDING').update(state='REVIEWED',reviewed_at=timezone.now(),confirmation_hash=hashlib.sha256(token.encode()).hexdigest(),review_device_id=device.pk if device else None)
    if changed!=1:raise TransferConflict()
    intent.refresh_from_db()
    return intent,token


@transaction.atomic
def execute(user,intent_id,digest,token,device_proof=None):
    intent=owned_intent(user,intent_id,digest)
    if not token or not hmac.compare_digest(hashlib.sha256(str(token).encode()).hexdigest(),intent.confirmation_hash):raise PermissionDenied('Segunda autorización inválida.')
    if intent.state=='EXECUTED':
        if intent.purpose:
            from .funded_refund import verify_posted
            verify_posted(intent)
        return intent
    if intent.state!='REVIEWED' or intent.expires_at<=timezone.now():raise TransferConflict('Se requieren dos autorizaciones vigentes y separadas.')
    if not intent.consent_at or intent.consent_digest!=intent.digest or not intent.consent_by_id:
        raise TransferConflict('Se requiere consentimiento explícito del destinatario para esta intención.')
    if getattr(settings,'WALLET_DEVICE_APPROVALS_REQUIRED',True):
        from .device_approvals import consume
        consume(user,intent,'EXECUTE',device_proof)
    wallets={wallet.pk:wallet for wallet in Wallet.objects.select_for_update().filter(pk__in=[intent.source_id,intent.destination_id]).order_by('pk')}
    source=wallets[intent.source_id];destination=wallets[intent.destination_id]
    from django.contrib.auth import get_user_model
    recipient=get_user_model().objects.filter(pk=intent.consent_by_id,is_active=True).first()
    if recipient is None:raise TransferConflict('El destinatario ya no está activo.')
    require_wallet_access(recipient,destination)
    check_wallets(user,source,destination,intent.amount)
    if source.currency!=intent.currency:raise TransferConflict('La moneda cambió después de preparar la operación.')
    if intent.purpose:
        from .funded_refund import validate_execution
        validate_execution(user,intent)
    if WalletTransferIntent.objects.filter(pk=intent.pk,state='REVIEWED').update(state='EXECUTED')!=1:raise TransferConflict()
    if Wallet.objects.filter(pk=source.pk,estado=Wallet.Status.ACTIVO,currency=intent.currency,saldo_disponible__gte=intent.amount).update(saldo_disponible=models.F('saldo_disponible')-intent.amount,updated_at=timezone.now())!=1:raise TransferConflict('El saldo disponible cambió.')
    if Wallet.objects.filter(pk=destination.pk,estado=Wallet.Status.ACTIVO,currency=intent.currency).update(saldo_disponible=models.F('saldo_disponible')+intent.amount,updated_at=timezone.now())!=1:raise TransferConflict()
    tx=WalletTransaccion.objects.create(referencia_operativa='INTERNAL-'+str(intent.pk),monto_total=intent.amount,estado=WalletTransaccion.Status.COMPLETADA,metadata={'kind':'INTERNAL_TRANSFER_V1','currency':intent.currency,'intent_id':str(intent.pk)})
    for wallet,kind in [(source,WalletMovimiento.TipoMovimiento.PAGO),(destination,WalletMovimiento.TipoMovimiento.INGRESO)]:
        WalletMovimiento.objects.create(wallet=wallet,transaccion=tx,tipo=kind,monto=intent.amount,referencia_modelo='InternalTransfer',referencia_id=str(intent.pk))
    if intent.purpose:
        from .funded_refund import post_accounting
        post_accounting(user,intent,tx)
    intent.transaction=tx;intent.executed_at=timezone.now();intent.state='EXECUTED';intent.save(update_fields=['transaction','executed_at','state'])
    return intent


@transaction.atomic
def consent(user,intent_id,digest,confirmed):
    principal(user)
    intent=get_object_or_404(WalletTransferIntent.objects.select_for_update(),pk=intent_id,destination__in=accessible_wallets(user))
    require_wallet_access(user,intent.destination)
    if confirmed is not True or intent.state not in {'PENDING','REVIEWED'} or intent.expires_at<=timezone.now() or digest!=intent.digest:
        raise TransferConflict('Consentimiento explícito vigente y resumen exacto requeridos.')
    intent.consent_by_id=user.pk;intent.consent_at=timezone.now();intent.consent_digest=digest
    intent.save(update_fields=['consent_by_id','consent_at','consent_digest'])
    return intent


@transaction.atomic
def cancel(user,intent_id,digest,confirmed):
    intent=owned_intent(user,intent_id,digest)
    if confirmed is not True or intent.state=='EXECUTED':raise TransferConflict('Una intención ejecutada no se cancela.')
    intent.state='CANCELLED';intent.confirmation_hash='';intent.review_device=None
    intent.save(update_fields=['state','confirmation_hash','review_device'])
    from ..models import WalletDeviceChallenge
    WalletDeviceChallenge.objects.filter(intent=intent,consumed_at__isnull=True,invalidated_at__isnull=True).update(invalidated_at=timezone.now())
    return intent


@transaction.atomic
def renew(user,intent_id,digest,key,confirmed):
    old=owned_intent(user,intent_id,digest)
    if confirmed is not True or old.state=='EXECUTED' or old.expires_at>timezone.now():raise TransferConflict('Solo se renuevan intenciones vencidas sin ejecutar.')
    existing=WalletTransferIntent.objects.filter(renewed_from=old).first()
    if existing:
        if existing.idempotency_key!=key:raise TransferConflict('La renovación ya existe; recupere su estado.')
        return existing
    if WalletTransferIntent.objects.filter(requested_by_id=user.pk,idempotency_key=key).exists():raise TransferConflict('La renovación necesita una clave nueva sin uso previo.')
    cancel(user,old.pk,digest,True)
    new=prepare(user,old.source_id,old.destination_id,old.amount,key)
    if new.renewed_from_id or new.state!='PENDING' or new.created_at<=old.created_at or new.purpose:raise TransferConflict('Clave de renovación ya utilizada.')
    new.purpose=dict(old.purpose)
    if new.purpose:
        new.purpose['requested_date']=timezone.localdate().isoformat()
        from .funded_refund import validate_execution
        validate_execution(user,new)
    new.digest=fingerprint(new.source_id,new.destination_id,new.amount,new.currency,new.purpose);new.renewed_from=old
    new.save(update_fields=['purpose','digest','renewed_from'])
    return new
