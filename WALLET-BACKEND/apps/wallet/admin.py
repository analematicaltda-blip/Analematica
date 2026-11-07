from django.contrib import admin
from .models import (
    Wallet, WalletTransaccion, WalletMovimiento, WalletBloqueo,
    WalletLiquidacion, WalletComision, WalletReversion, WalletAuditoria,
    WalletLimiteOperativo, WalletAlertaRiesgo, WalletDeviceCredential, WalletDeviceChallenge
)

class ReadOnlyWalletAdmin(admin.ModelAdmin):
    # Generic Django staff/superuser status is not a company-wallet mandate.
    # Financial operations use the scoped API, never the global admin console.
    def has_module_permission(self,request):return False
    def has_view_permission(self,request,obj=None):return False
    def get_queryset(self,request):return super().get_queryset(request).none()
    def has_add_permission(self,request):return False
    def has_change_permission(self,request,obj=None):return False
    def has_delete_permission(self,request,obj=None):return False

@admin.register(WalletDeviceCredential)
class WalletDeviceCredentialAdmin(ReadOnlyWalletAdmin):
    list_display=('id','user_id','status','valid_until','revoked_at')
    def get_queryset(self,request):
        query=super().get_queryset(request)
        return query.none()

@admin.register(WalletDeviceChallenge)
class WalletDeviceChallengeAdmin(ReadOnlyWalletAdmin):
    list_display=('id','intent','phase','expires_at','consumed_at','invalidated_at')
    def get_queryset(self,request):
        query=super().get_queryset(request)
        return query.none()

@admin.register(Wallet)
class WalletAdmin(ReadOnlyWalletAdmin):
    list_display = ('id', 'user_id', 'owner_type', 'owner_id', 'saldo_disponible', 'estado')
    list_filter = ('owner_type', 'estado')
    search_fields = ('user_id', 'owner_id')

@admin.register(WalletTransaccion)
class WalletTransaccionAdmin(ReadOnlyWalletAdmin):
    list_display = ('id', 'referencia_operativa', 'monto_total', 'estado', 'timestamp')
    list_filter = ('estado',)
    search_fields = ('id', 'referencia_operativa')

@admin.register(WalletMovimiento)
class WalletMovimientoAdmin(ReadOnlyWalletAdmin):
    list_display = ('id', 'wallet', 'transaccion', 'tipo', 'monto', 'timestamp')
    list_filter = ('tipo',)
    search_fields = ('wallet__owner_id', 'referencia_id')

@admin.register(WalletBloqueo)
class WalletBloqueoAdmin(ReadOnlyWalletAdmin):
    list_display = ('id', 'wallet', 'monto', 'motivo', 'activo')
    list_filter = ('activo',)

@admin.register(WalletLiquidacion)
class WalletLiquidacionAdmin(ReadOnlyWalletAdmin):
    list_display = ('id', 'wallet', 'monto', 'periodo_fin')

@admin.register(WalletComision)
class WalletComisionAdmin(ReadOnlyWalletAdmin):
    list_display = ('id', 'transaccion', 'receptor_wallet', 'monto', 'porcentaje')

@admin.register(WalletReversion)
class WalletReversionAdmin(ReadOnlyWalletAdmin):
    list_display = ('id', 'transaccion_original', 'autorizado_por_id', 'timestamp')

@admin.register(WalletAuditoria)
class WalletAuditoriaAdmin(ReadOnlyWalletAdmin):
    list_display = ('id', 'wallet', 'tipo_hallazgo', 'nivel_riesgo', 'timestamp')
    list_filter = ('nivel_riesgo',)

@admin.register(WalletLimiteOperativo)
class WalletLimiteOperativoAdmin(ReadOnlyWalletAdmin):
    list_display = ('wallet', 'monto_maximo_transaccion', 'requiere_aprobacion_soberana')

@admin.register(WalletAlertaRiesgo)
class WalletAlertaRiesgoAdmin(ReadOnlyWalletAdmin):
    list_display = ('wallet', 'codigo_alerta', 'atendida', 'timestamp')
    list_filter = ('atendida', 'codigo_alerta')
