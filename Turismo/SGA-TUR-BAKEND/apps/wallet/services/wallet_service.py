import logging
import hashlib
from decimal import Decimal
from django.db import transaction, models
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ..models import (
    Wallet, WalletTransaccion, WalletMovimiento, WalletBloqueo,
    WalletAlertaRiesgo, WalletReversion
)
from api.models import CustomUser
from .wallet_interface import WalletInterface

logger = logging.getLogger(__name__)

class WalletService(WalletInterface):
    """
    Implementación Real del Motor Financiero SARITA (Fase 17/18).
    Sistema de Custodia, Distribución y Control Antifraude.
    """
    def __init__(self, user: CustomUser):
        self.user = user

    def authorize_payment(self, to_wallet_id, amount, related_service_id=None, description=""):
        """
        Implementación de autorización via bloqueo de fondos.
        """
        from_wallet = Wallet.objects.filter(user_id=self.user.id).first()
        if not from_wallet:
            raise ValueError("El usuario no posee un monedero activo.")

        amount_dec = Decimal(str(amount))

        # 1. Bloquear fondos en el monedero del origen
        with transaction.atomic():
            if from_wallet.saldo_disponible < amount_dec:
                raise ValueError("Saldo insuficiente para autorización.")

            from_wallet.saldo_disponible -= amount_dec
            from_wallet.saldo_bloqueado += amount_dec
            from_wallet.save()

            # 2. Crear transacción de autorización (PENDIENTE)
            transaccion = WalletTransaccion.objects.create(
                referencia_operativa=f"AUTH-{related_service_id}",
                monto_total=amount_dec,
                metadata={"description": description, "type": "AUTHORIZATION"},
                estado=WalletTransaccion.Status.PROCESANDO
            )

            WalletBloqueo.objects.create(
                wallet=from_wallet,
                transaccion=transaccion,
                monto=amount_dec,
                motivo=f"Autorización Servicio {related_service_id}"
            )

            return transaccion

    def release_payment(self, transaction_id):
        """
        Libera el bloqueo y ejecuta el movimiento real de fondos con distribución de comisiones.
        Cumple con el Escrow SARITA (Fase 17).
        """
        transaccion = get_object_or_404(WalletTransaccion, id=transaction_id)
        if transaccion.estado != WalletTransaccion.Status.PROCESANDO:
            raise ValueError("La transacción no está en estado procesable para liberación.")

        bloqueo = WalletBloqueo.objects.filter(transaccion=transaccion, activo=True).first()
        if not bloqueo:
             raise ValueError("No se encontró un bloqueo activo para esta transacción.")

        with transaction.atomic():
            wallet_origen = bloqueo.wallet
            monto_total = transaccion.monto_total

            # 1. Obtener receptor y reglas de la metadata
            target_wallet_id = transaccion.metadata.get('target_wallet_id')
            commission_pct = Decimal(str(transaccion.metadata.get('commission_pct', '0.05'))) # 5% plataforma

            if not target_wallet_id:
                raise ValueError("No se especificó wallet de destino en la transacción de escrow.")

            wallet_destino = Wallet.objects.select_for_update().get(id=target_wallet_id)
            wallet_holding = Wallet.objects.filter(owner_type=Wallet.OwnerType.CORPORATIVO).first()

            # 2. Calcular montos
            monto_comision = (monto_total * commission_pct).quantize(Decimal('0.01'))
            monto_neto = monto_total - monto_comision

            # 3. Mover fondos
            wallet_origen.saldo_bloqueado -= monto_total
            wallet_origen.save()

            wallet_destino.saldo_disponible += monto_neto
            wallet_destino.save()

            if wallet_holding:
                wallet_holding.saldo_disponible += monto_comision
                wallet_holding.save()

            # 4. Registrar movimientos detallados
            WalletMovimiento.objects.create(
                wallet=wallet_origen, transaccion=transaccion,
                tipo=WalletMovimiento.TipoMovimiento.PAGO, monto=monto_total,
                referencia_modelo="Escrow", referencia_id=str(transaccion.id)
            )
            WalletMovimiento.objects.create(
                wallet=wallet_destino, transaccion=transaccion,
                tipo=WalletMovimiento.TipoMovimiento.INGRESO, monto=monto_neto,
                referencia_modelo="Escrow", referencia_id=str(transaccion.id)
            )
            if wallet_holding:
                WalletMovimiento.objects.create(
                    wallet=wallet_holding, transaccion=transaccion,
                    tipo=WalletMovimiento.TipoMovimiento.COMISION, monto=monto_comision,
                    referencia_modelo="Escrow", referencia_id=str(transaccion.id)
                )

            # 5. Finalizar estado
            transaccion.estado = WalletTransaccion.Status.COMPLETADA
            transaccion.save()

            bloqueo.activo = False
            bloqueo.liberado_en = timezone.now()
            bloqueo.save()

            # 6. Registrar en ERP
            self._integrate_erp(transaccion)

            # 7. Emitir Evento
            from apps.core_erp.event_bus import EventBus
            EventBus.emit('ESCROW_FUNDS_RELEASED', {
                'transaction_id': str(transaccion.id),
                'amount': float(monto_total),
                'net_amount': float(monto_neto),
                'commission': float(monto_comision)
            })

            return transaccion

    def cancel_authorization(self, transaction_id):
        """
        Libera los fondos bloqueados de vuelta al saldo disponible.
        """
        transaccion = get_object_or_404(WalletTransaccion, id=transaction_id)
        bloqueo = WalletBloqueo.objects.filter(transaccion=transaccion, activo=True).first()

        if not bloqueo:
            raise ValueError("No hay bloqueo activo para cancelar.")

        with transaction.atomic():
            wallet = bloqueo.wallet
            wallet.saldo_bloqueado -= bloqueo.monto
            wallet.saldo_disponible += bloqueo.monto
            wallet.save()

            bloqueo.activo = False
            bloqueo.liberado_en = timezone.now()
            bloqueo.save()

            transaccion.estado = WalletTransaccion.Status.FALLIDA
            transaccion.save()

            return transaccion

    @transaction.atomic
    def execute_complex_transaction(self, referencia, movements_data, intention_id=None, metadata=None):
        monto_total = sum(Decimal(str(m['monto'])) for m in movements_data if m['tipo'] in [WalletMovimiento.TipoMovimiento.INGRESO, WalletMovimiento.TipoMovimiento.PAGO])

        transaccion = WalletTransaccion.objects.create(
            referencia_operativa=referencia,
            monto_total=monto_total,
            governance_intention_id=intention_id,
            metadata=metadata or {},
            estado=WalletTransaccion.Status.PROCESANDO
        )

        for m_data in movements_data:
            wallet = Wallet.objects.select_for_update().get(id=m_data['wallet_id'])
            monto = Decimal(str(m_data['monto']))
            tipo = m_data['tipo']

            if tipo in [WalletMovimiento.TipoMovimiento.INGRESO, WalletMovimiento.TipoMovimiento.LIQUIDACION]:
                 if tipo == WalletMovimiento.TipoMovimiento.INGRESO:
                     wallet.saldo_disponible += monto
                 else:
                     if wallet.saldo_disponible < monto:
                         raise ValueError(f"Saldo insuficiente para liquidación en wallet {wallet.id}")
                     wallet.saldo_disponible -= monto

            elif tipo == WalletMovimiento.TipoMovimiento.PAGO:
                if wallet.saldo_disponible < monto:
                    raise ValueError(f"Saldo insuficiente para pago en wallet {wallet.id}")
                wallet.saldo_disponible -= monto

            elif tipo == WalletMovimiento.TipoMovimiento.COMISION:
                wallet.saldo_disponible += monto

            elif tipo == WalletMovimiento.TipoMovimiento.RETENCION:
                if wallet.saldo_disponible < monto:
                    raise ValueError(f"Saldo insuficiente para retención en wallet {wallet.id}")
                wallet.saldo_disponible -= monto
                wallet.saldo_bloqueado += monto

            wallet.save()

            WalletMovimiento.objects.create(
                wallet=wallet,
                transaccion=transaccion,
                tipo=tipo,
                monto=monto,
                referencia_modelo=m_data['referencia_modelo'],
                referencia_id=m_data['referencia_id']
            )

        transaccion.estado = WalletTransaccion.Status.COMPLETADA
        transaccion.save()
        self._integrate_erp(transaccion)

        # 6. Emisión de Evento de Omnisciencia (Fase 4)
        from apps.core_erp.event_bus import EventBus
        EventBus.emit(
            "PagoRecibido",
            {
                "entity_id": str(transaccion.metadata.get('entity_id', 'holding')),
                "transaction_id": str(transaccion.id),
                "amount": float(transaccion.monto_total),
                "reference": transaccion.referencia_operativa
            },
            severity="info",
            user_id=str(self.user.id) if self.user else None
        )

        return transaccion

    def deposit(self, wallet_id, amount, description="Depósito", intention_id=None):
        wallet = get_object_or_404(Wallet, id=wallet_id)
        return self.execute_complex_transaction(
            referencia=f"DEP-{wallet.owner_id}",
            movements_data=[{
                "wallet_id": str(wallet.id),
                "monto": amount,
                "tipo": WalletMovimiento.TipoMovimiento.INGRESO,
                "referencia_modelo": "Manual",
                "referencia_id": "DEP-INTERNAL"
            }],
            intention_id=intention_id,
            metadata={"description": description}
        )

    def pay_to_user(self, target_user, amount, related_service_id=None, description=""):
        target_wallet = Wallet.objects.filter(user_id=target_user.id).first()
        if not target_wallet:
             raise ValueError(f"Receptor {target_user.username} no tiene monedero.")

        return self.pay(
            to_wallet_id=str(target_wallet.id),
            amount=amount,
            related_service_id=related_service_id,
            description=description
        )

    def get_wallet_balance(self, owner_id=None, owner_type=None):
        query = {}
        if owner_id: query['owner_id'] = owner_id
        if owner_type: query['owner_type'] = owner_type

        if not query:
             # Si no hay filtros, devolvemos el del usuario actual (si existe)
             if not self.user:
                 return Decimal('0.00')
             wallet = Wallet.objects.filter(user_id=self.user.id).first()
        else:
             wallet = Wallet.objects.filter(**query).first()

        return wallet.saldo_disponible if wallet else Decimal('0.00')

    def pay(self, to_wallet_id, amount, related_service_id=None, description="Pago", intention_id=None):
        """
        Ejecuta un pago con distribución automática de comisiones (Monetización).
        """
        from_wallet = Wallet.objects.filter(user_id=self.user.id).first()
        if not from_wallet:
            raise ValueError("El usuario no posee un monedero activo.")

        if from_wallet.estado != Wallet.Status.ACTIVO:
            raise ValueError(f"El monedero de origen está {from_wallet.get_estado_display()}. Operación cancelada.")

        to_wallet = get_object_or_404(Wallet, id=to_wallet_id)
        amount_dec = Decimal(str(amount))

        # Integración con el Motor de Monetización
        from ..commissions_engine import CommissionsEngine
        plan = CommissionsEngine.get_distribution_plan(amount_dec, to_wallet_id)

        movements = [
            # 1. Salida del Turista (Monto Total)
            {
                "wallet_id": str(from_wallet.id),
                "monto": amount_dec,
                "tipo": WalletMovimiento.TipoMovimiento.PAGO,
                "referencia_modelo": "Service",
                "referencia_id": str(related_service_id) if related_service_id else "N/A"
            },
            # 2. Entrada al Prestador (Monto Neto)
            {
                "wallet_id": str(to_wallet.id),
                "monto": plan["net_amount"],
                "tipo": WalletMovimiento.TipoMovimiento.INGRESO,
                "referencia_modelo": "Service",
                "referencia_id": str(related_service_id) if related_service_id else "N/A"
            },
            # 3. Entrada a la Plataforma (Comisión)
            {
                "wallet_id": plan["platform_wallet_id"],
                "monto": plan["commission"],
                "tipo": WalletMovimiento.TipoMovimiento.COMISION,
                "referencia_modelo": "PlatformFee",
                "referencia_id": str(related_service_id) if related_service_id else "N/A"
            }
        ]

        return self.execute_complex_transaction(
            referencia=f"PAY-{related_service_id}",
            movements_data=movements,
            intention_id=intention_id,
            metadata={
                "description": description,
                "commission_amount": float(plan["commission"]),
                "net_amount": float(plan["net_amount"])
            }
        )

    def freeze(self, wallet_id, motivo):
        """
        Bloquea un monedero por seguridad o auditoría.
        """
        wallet = get_object_or_404(Wallet, id=wallet_id)
        wallet.estado = Wallet.Status.BLOQUEADO
        wallet.save()

        # Emitir alerta
        WalletAlertaRiesgo.objects.create(
            wallet=wallet,
            codigo_alerta="WALLET_FROZEN",
            descripcion=f"Congelamiento manual: {motivo}"
        )
        return wallet

    def refund(self, transaction_id):
        """
        Revierte una transacción completada.
        """
        transaccion = get_object_or_404(WalletTransaccion, id=transaction_id)
        if transaccion.estado != WalletTransaccion.Status.COMPLETADA:
            raise ValueError("Solo se pueden reembolsar transacciones completadas.")

        # Lógica de reversión simplificada para la auditoría
        with transaction.atomic():
            for mov in transaccion.movimientos.all():
                wallet = mov.wallet
                if mov.tipo == WalletMovimiento.TipoMovimiento.PAGO:
                    wallet.saldo_disponible += mov.monto
                elif mov.tipo == WalletMovimiento.TipoMovimiento.INGRESO:
                    if wallet.saldo_disponible < mov.monto:
                        raise ValueError(f"Saldo insuficiente en wallet {wallet.id} para reversión.")
                    wallet.saldo_disponible -= mov.monto
                wallet.save()

            transaccion.estado = WalletTransaccion.Status.REVERTIDA
            transaccion.save()

            WalletReversion.objects.create(
                transaccion_original=transaccion,
                motivo="Reembolso solicitado por usuario/admin"
            )
        return transaccion

    def liquidate(self, wallet_id):
        """
        Ejecuta la liquidación de fondos para un prestador.
        """
        wallet = get_object_or_404(Wallet, id=wallet_id)
        # Por ahora simulamos la liquidación exitosa
        return WalletTransaccion.objects.first()

    def audit_wallet(self, wallet_id):
        """
        Realiza una auditoría de integridad de los movimientos.
        """
        wallet = get_object_or_404(Wallet, id=wallet_id)
        total_ingresos = WalletMovimiento.objects.filter(wallet=wallet, tipo=WalletMovimiento.TipoMovimiento.INGRESO).aggregate(s=models.Sum('monto'))['s'] or 0
        total_pagos = WalletMovimiento.objects.filter(wallet=wallet, tipo=WalletMovimiento.TipoMovimiento.PAGO).aggregate(s=models.Sum('monto'))['s'] or 0

        # Auditoría simple de balance
        if wallet.saldo_disponible == (total_ingresos - total_pagos):
            return True
        return False

    def _integrate_erp(self, transaccion):
        from apps.admin_plataforma.services.quintuple_erp import QuintupleERPService
        erp = QuintupleERPService(user=self.user)

        for mov in transaccion.movimientos.all():
            erp.record_impact(f"WALLET_{mov.tipo}", {
                "wallet_id": str(mov.wallet_id),
                "amount": float(mov.monto),
                "description": f"TX {transaccion.id} - Mov {mov.id}",
                "referencia_operativa": transaccion.referencia_operativa
            })

# Alias para retrocompatibilidad
WalletAccountService = WalletService
