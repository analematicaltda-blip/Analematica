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


class TransferConflict(APIException):
    status_code=409
    default_code='wallet_transfer_conflict'
    default_detail='El estado del monedero o de la autorización cambió.'


def principal(user):
    if not user or not user.is_authenticated or not user.is_active:
        raise PermissionDenied('Sesión activa requerida.')
    if not (user.is_superuser or getattr(user,'role','') in {'BUSINESS_OWNER','BUSINESS_ADMIN','PRESTADOR','ADMIN'}):
        raise PermissionDenied('Se requiere un administrador autorizado.')
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


def fingerprint(source,destination,amount,currency):
    data={'source':str(source),'destination':str(destination),'amount':str(amount),'currency':currency}
    return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def check_wallets(user,source,destination,amount):
    if source.user_id!=user.pk:raise PermissionDenied('El monedero de origen no le pertenece.')
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
    source=get_object_or_404(Wallet,user_id=user.pk,pk=source_id)
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
    expected=fingerprint(intent.source_id,intent.destination_id,intent.amount,intent.currency)
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
    if intent.state=='EXECUTED':return intent
    if intent.state!='REVIEWED' or intent.expires_at<=timezone.now():raise TransferConflict('Se requieren dos autorizaciones vigentes y separadas.')
    if getattr(settings,'WALLET_DEVICE_APPROVALS_REQUIRED',True):
        from .device_approvals import consume
        consume(user,intent,'EXECUTE',device_proof)
    wallets={wallet.pk:wallet for wallet in Wallet.objects.select_for_update().filter(pk__in=[intent.source_id,intent.destination_id]).order_by('pk')}
    source=wallets[intent.source_id];destination=wallets[intent.destination_id]
    check_wallets(user,source,destination,intent.amount)
    if source.currency!=intent.currency:raise TransferConflict('La moneda cambió después de preparar la operación.')
    if WalletTransferIntent.objects.filter(pk=intent.pk,state='REVIEWED').update(state='EXECUTED')!=1:raise TransferConflict()
    if Wallet.objects.filter(pk=source.pk,estado=Wallet.Status.ACTIVO,currency=intent.currency,saldo_disponible__gte=intent.amount).update(saldo_disponible=models.F('saldo_disponible')-intent.amount,updated_at=timezone.now())!=1:raise TransferConflict('El saldo disponible cambió.')
    if Wallet.objects.filter(pk=destination.pk,estado=Wallet.Status.ACTIVO,currency=intent.currency).update(saldo_disponible=models.F('saldo_disponible')+intent.amount,updated_at=timezone.now())!=1:raise TransferConflict()
    tx=WalletTransaccion.objects.create(referencia_operativa='INTERNAL-'+str(intent.pk),monto_total=intent.amount,estado=WalletTransaccion.Status.COMPLETADA,metadata={'kind':'INTERNAL_TRANSFER_V1','currency':intent.currency,'intent_id':str(intent.pk)})
    for wallet,kind in [(source,WalletMovimiento.TipoMovimiento.PAGO),(destination,WalletMovimiento.TipoMovimiento.INGRESO)]:
        WalletMovimiento.objects.create(wallet=wallet,transaccion=tx,tipo=kind,monto=intent.amount,referencia_modelo='InternalTransfer',referencia_id=str(intent.pk))
    intent.transaction=tx;intent.executed_at=timezone.now();intent.state='EXECUTED';intent.save(update_fields=['transaction','executed_at','state'])
    return intent
