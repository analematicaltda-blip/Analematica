"""Legacy monetary entry points fail closed until externally reconciled adapters exist."""
from decimal import Decimal
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import APIException, PermissionDenied
from ..models import Wallet
from .wallet_interface import WalletInterface


class WalletOperationUnavailable(APIException):
    status_code=503
    default_code='wallet_operation_not_enabled'
    default_detail='Esta operación requiere un adaptador conciliado. No se movieron fondos. Use el flujo interno de doble autorización cuando esté habilitado.'


class WalletService(WalletInterface):
    def __init__(self,user):
        self.user=user

    def _disabled(self,*args,**kwargs):
        raise WalletOperationUnavailable()

    authorize_payment=_disabled
    release_payment=_disabled
    cancel_authorization=_disabled
    execute_complex_transaction=_disabled
    deposit=_disabled
    pay_to_user=_disabled
    pay=_disabled
    freeze=_disabled
    refund=_disabled
    liquidate=_disabled
    audit_wallet=_disabled

    def get_wallet_balance(self,owner_id=None,owner_type=None):
        if not self.user or not self.user.is_authenticated or not self.user.is_active:
            raise PermissionDenied('Sesión activa requerida.')
        query=Wallet.objects.filter(user_id=self.user.pk)
        if owner_id is not None:query=query.filter(owner_id=owner_id)
        if owner_type is not None:query=query.filter(owner_type=owner_type)
        if query.count()>1:raise PermissionDenied('Seleccione un monedero propio explícitamente.')
        return get_object_or_404(query).saldo_disponible


WalletAccountService=WalletService
