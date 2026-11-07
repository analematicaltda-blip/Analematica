from django.contrib import admin
from .models import (
    Wallet, WalletTransaccion, WalletMovimiento, WalletBloqueo,
    WalletLiquidacion, WalletComision, WalletReversion, WalletAuditoria,
    WalletLimiteOperativo, WalletAlertaRiesgo
)

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'owner_type', 'owner_id', 'saldo_disponible', 'estado')
    list_filter = ('owner_type', 'estado')
    search_fields = ('user_id', 'owner_id')

@admin.register(WalletTransaccion)
class WalletTransaccionAdmin(admin.ModelAdmin):
    list_display = ('id', 'referencia_operativa', 'monto_total', 'estado', 'timestamp')
    list_filter = ('estado',)
    search_fields = ('id', 'referencia_operativa')

@admin.register(WalletMovimiento)
class WalletMovimientoAdmin(admin.ModelAdmin):
    list_display = ('id', 'wallet', 'transaccion', 'tipo', 'monto', 'timestamp')
    list_filter = ('tipo',)
    search_fields = ('wallet__owner_id', 'referencia_id')

@admin.register(WalletBloqueo)
class WalletBloqueoAdmin(admin.ModelAdmin):
    list_display = ('id', 'wallet', 'monto', 'motivo', 'activo')
    list_filter = ('activo',)

@admin.register(WalletLiquidacion)
class WalletLiquidacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'wallet', 'monto', 'periodo_fin')

@admin.register(WalletComision)
class WalletComisionAdmin(admin.ModelAdmin):
    list_display = ('id', 'transaccion', 'receptor_wallet', 'monto', 'porcentaje')

@admin.register(WalletReversion)
class WalletReversionAdmin(admin.ModelAdmin):
    list_display = ('id', 'transaccion_original', 'autorizado_por_id', 'timestamp')

@admin.register(WalletAuditoria)
class WalletAuditoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'wallet', 'tipo_hallazgo', 'nivel_riesgo', 'timestamp')
    list_filter = ('nivel_riesgo',)

@admin.register(WalletLimiteOperativo)
class WalletLimiteOperativoAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'monto_maximo_transaccion', 'requiere_aprobacion_soberana')

@admin.register(WalletAlertaRiesgo)
class WalletAlertaRiesgoAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'codigo_alerta', 'atendida', 'timestamp')
    list_filter = ('atendida', 'codigo_alerta')
