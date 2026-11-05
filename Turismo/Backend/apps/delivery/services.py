import logging
from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.db import transaction, models
from .models import DeliveryCompany, Driver, Vehicle, DeliveryService, DeliveryEvent
from api.models import CustomUser
from apps.wallet.services import WalletService

logger = logging.getLogger(__name__)

class DeliveryLogisticService:
    """ Motor Logístico SARITA (Fase 9 & 18) """
    def __init__(self, user: CustomUser = None):
        self.user = user

    def create_request(self, parameters, intention_id=None):
        with transaction.atomic():
            service = DeliveryService.objects.create(
                tourist_id=self.user.id if self.user else parameters.get('user_id'),
                origin_address=parameters["origin_address"],
                destination_address=parameters["destination_address"],
                estimated_price=parameters.get("estimated_price", 0),
                value_declared=parameters.get("value_declared", 0),
                governance_intention_id=intention_id,
                status=DeliveryService.Status.PENDIENTE,
                related_operational_order_id=parameters.get("related_operational_order_id"),
                provider_id=parameters.get("provider_id"),
                prioridad=parameters.get("prioridad", "NORMAL")
            )

            # Crear ítems si vienen en la data
            items_data = parameters.get("items", [])
            for item in items_data:
                from .models import DeliveryItem
                DeliveryItem.objects.create(
                    delivery=service,
                    product_id=item.get("product_id"),
                    description=item.get("description"),
                    quantity=item.get("quantity", 1),
                    weight_kg=Decimal(str(item.get("weight_kg", 0))),
                    is_fragile=item.get("is_fragile", False),
                    requires_cold_chain=item.get("requires_cold_chain", False)
                )

            DeliveryEvent.objects.create(
                service=service,
                event_type="REQUEST_CREATED",
                description=f"Pedido de delivery creado."
            )

            # --- IMPACTO ERP QUÍNTUPLE (FASE 9) ---
            self._propagate_erp_impact(service, "DELIVERY_REQUESTED")

            return service

    def assign_service(self, service_id, driver_id=None):
        # S-1.1: Soportar parámetros como dict o valor directo (Compatibilidad Kernel)
        if isinstance(service_id, dict):
            params = service_id
            service_id = params.get("service_id")
            driver_id = params.get("driver_id")

        service = get_object_or_404(DeliveryService, id=service_id)

        # Asignación Automática si no viene driver_id (Motor Logístico Real 100%)
        if not driver_id:
            # Algoritmo de cercanía o disponibilidad
            driver = Driver.objects.filter(
                is_available=True,
                delivery_company__is_active=True
            ).order_by('?').first() # Por ahora aleatorio para evitar sesgo

            if not driver:
                logger.warning(f"DELIVERY: No hay repartidores disponibles para el servicio {service_id}")
                return None
        else:
            driver = get_object_or_404(Driver, id=driver_id)

        vehicle = Vehicle.objects.filter(delivery_company=driver.delivery_company, is_active=True).first()

        with transaction.atomic():
            service.driver = driver
            service.vehicle = vehicle
            service.delivery_company = driver.delivery_company
            service.status = DeliveryService.Status.LISTO_DESPACHO

            # Asignación de Ruta (Si no tiene una asignada)
            if not service.ruta:
                from .models import Ruta
                # Buscar ruta activa en la zona o crear una nueva
                ruta = Ruta.objects.filter(zona=service.origin_address[:20], activa=True).first()
                if not ruta:
                    ruta = Ruta.objects.create(
                        nombre=f"Ruta {service.origin_address[:20]}",
                        zona=service.origin_address[:20],
                        repartidor=driver
                    )
                service.ruta = ruta

            service.save()

            driver.is_available = False
            driver.save()

            DeliveryEvent.objects.create(
                service=service,
                event_type="ASSIGNED",
                description=f"Repartidor {driver.user.username if driver.user else 'N/A'} asignado."
            )

            self._propagate_erp_impact(service, "DELIVERY_ASSIGNED")

            return service

    def start_delivery(self, service_id):
        service = get_object_or_404(DeliveryService, id=service_id)
        service.status = DeliveryService.Status.EN_RUTA
        service.save()

        DeliveryEvent.objects.create(service=service, event_type="IN_ROUTE", description="Pedido en ruta.")
        return service

    def fail_delivery(self, service_id, reason, severity='MEDIUM'):
        service = get_object_or_404(DeliveryService, id=service_id)
        service.status = DeliveryService.Status.FALLIDO
        service.save()

        from .models import DeliveryIncident
        DeliveryIncident.objects.create(
            delivery=service,
            description=reason,
            severity=severity
        )

        DeliveryEvent.objects.create(service=service, event_type="FAILED", description=f"Falla: {reason}")
        return service

    def report_incident(self, service_id, description, severity='MEDIUM'):
        service = get_object_or_404(DeliveryService, id=service_id)
        service.status = DeliveryService.Status.EN_INCIDENCIA
        service.save()

        from .models import DeliveryIncident
        incident = DeliveryIncident.objects.create(
            delivery=service,
            description=description,
            severity=severity
        )

        DeliveryEvent.objects.create(service=service, event_type="INCIDENT_REPORTED", description=description)
        return incident

    def reject_delivery(self, service_id, reason):
        service = get_object_or_404(DeliveryService, id=service_id)
        service.status = DeliveryService.Status.RECHAZADA
        service.save()

        from .models import DeliveryIncident
        DeliveryIncident.objects.create(
            delivery=service,
            description=f"Rechazo por cliente: {reason}",
            severity='HIGH'
        )

        DeliveryEvent.objects.create(service=service, event_type="REJECTED", description=reason)

        # --- IMPACTO ERP REVERSO (Si aplica) ---
        self._propagate_erp_impact(service, "DELIVERY_REJECTED")

        return service

    def complete_service(self, service_id, parameters=None):
        service = get_object_or_404(DeliveryService, id=service_id)

        if service.status == DeliveryService.Status.ENTREGADO:
            return service

        # FASE 18: Exigir evidencia obligatoria (Ruptura 3.1)
        if not parameters or (not parameters.get("firma") and not parameters.get("foto")):
             raise ValueError("No se puede marcar como entregado sin evidencia (Firma o Foto).")

        # Verificar si hay incidencias críticas abiertas
        if service.incidents.filter(severity='CRITICAL', is_resolved=False).exists():
            raise ValueError("No se puede completar el servicio con incidencias críticas pendientes.")

        with transaction.atomic():
            service.status = DeliveryService.Status.ENTREGADO
            service.final_price = service.estimated_price
            # Cálculo de Comisión Repartidor (15% por defecto para Fase 9)
            service.comision_repartidor = service.final_price * Decimal('0.15')
            service.save()

            from .models import EvidenciaEntrega
            EvidenciaEntrega.objects.create(
                delivery=service,
                firma_digital=parameters.get("firma", ""),
                observaciones=parameters.get("observaciones", ""),
                latitud=parameters.get("latitud"),
                longitud=parameters.get("longitud")
            )

            DeliveryEvent.objects.create(
                service=service,
                event_type="COMPLETED",
                description="Entrega confirmada."
            )

            if service.driver:
                service.driver.is_available = True
                service.driver.save()

            # --- LIQUIDACIÓN LOGÍSTICA ---
            self.liquidate_service(service.id)

            # --- INTEGRACIÓN CON MONEDERO (PAGO OBLIGATORIO) ---
            self._process_payment(service)
            self._propagate_erp_impact(service, "DELIVERY_COMPLETED")

            return service

    def liquidate_service(self, service_id):
        """
        Capa financiera del delivery (Fase 18).
        """
        service = get_object_or_404(DeliveryService, id=service_id)
        if service.status != DeliveryService.Status.ENTREGADO:
             raise ValueError("Solo se pueden liquidar servicios entregados.")

        from .models import DeliveryLiquidation
        if hasattr(service, 'liquidation'):
             raise ValueError("El servicio ya ha sido liquidado.")

        total = service.final_price
        commission = service.comision_repartidor
        platform_fee = total * Decimal('0.05') # 5% plataforma

        liquidation = DeliveryLiquidation.objects.create(
            delivery=service,
            total_to_provider=total - commission - platform_fee,
            total_to_driver=commission,
            platform_fee=platform_fee,
            is_processed=True
        )
        return liquidation

    def rate_service(self, service_id, rating, comment=""):
        service = get_object_or_404(DeliveryService, id=service_id)
        if service.status != DeliveryService.Status.ENTREGADO:
            raise ValueError("Solo se pueden calificar servicios entregados.")

        service.rating = rating
        service.tourist_comment = comment
        service.save()

        # Actualizar reputación del conductor
        if service.driver:
            driver = service.driver
            avg_rating = DeliveryService.objects.filter(driver=driver, rating__isnull=False).aggregate(models.Avg('rating'))['rating__avg']
            if avg_rating:
                driver.reputation = Decimal(str(avg_rating))
                driver.save()

        logger.info(f"DELIVERY: Servicio {service_id} calificado con {rating}")
        return service

    def penalize_driver(self, driver_id, amount, reason, service_id=None):
        """
        Aplica una penalización económica a un transportista (Fase 18).
        """
        from .models import DeliveryPenalty, Driver
        driver = get_object_or_404(Driver, id=driver_id)

        penalty = DeliveryPenalty.objects.create(
            driver=driver,
            delivery_id=service_id,
            amount=Decimal(str(amount)),
            reason=reason
        )

        # Impacto en reputación
        driver.reputation -= Decimal('0.5')
        if driver.reputation < 0: driver.reputation = 0
        driver.save()

        logger.warning(f"DELIVERY: Conductor {driver_id} penalizado con {amount}. Motivo: {reason}")
        return penalty

    def _propagate_erp_impact(self, service, event_type):
        """Propaga el impacto a las 5 dimensiones del ERP."""
        from apps.admin_plataforma.services.quintuple_erp import QuintupleERPService
        erp_service = QuintupleERPService(user=self.user)

        payload = {
            "company_id": str(service.delivery_company.company.id) if (service.delivery_company and service.delivery_company.company) else None,
            "perfil_id": str(service.provider_id) if service.provider_id else None,
            "cliente_id": str(service.tourist_id),
            "amount": float(service.final_price or service.estimated_price),
            "description": f"Servicio Delivery {service.id} - {event_type}",
            "delivery_service_id": str(service.id),
            "reserva_id": str(service.related_operational_order_id) if service.related_operational_order_id else None,
            "wallet_transaction_id": str(service.wallet_transaction) if service.wallet_transaction else None
        }

        erp_service.record_impact(event_type, payload)

    def _process_payment(self, service):
        """
        Ejecuta el pago real desde el monedero del turista al monedero de la empresa/conductor.
        (Fase 18: Desacoplamiento via WalletService sin tocar modelos de wallet).
        """
        from api.models import CustomUser
        tourist = CustomUser.objects.get(id=service.tourist_id)
        wallet_service = WalletService(user=tourist)

        # Determinar el usuario receptor
        target_user = None
        if service.driver:
            target_user = service.driver.user

        if not target_user:
            logger.warning(f"PAGO DELIVERY: No se puede procesar pago sin receptor asignado en servicio {service.id}")
            return

        try:
            # Ejecutar pago via monedero gobernado (Resolución de monedero interna al servicio)
            tx_result = wallet_service.pay_to_user(
                target_user=target_user,
                amount=service.final_price,
                related_service_id=service.id,
                description=f"Pago por servicio de Delivery {service.id}"
            )

            service.wallet_transaction = tx_result.id
            service.save()
            logger.info(f"PAGO DELIVERY: Procesado para servicio {service.id} via TX {tx_result.id}")

        except Exception as e:
            logger.error(f"PAGO DELIVERY: Error procesando pago: {e}")

    @staticmethod
    def generar_indicadores(provider_id):
        """ Genera KPIs de Delivery para un Tenant """
        from .models import IndicadorLogistico, DeliveryService
        from django.db.models import Avg, Count, F, Sum
        from django.utils import timezone

        periodo = timezone.now().strftime("%Y-%m")

        # 1. Tiempo Promedio de Entrega (Simulado para Fase 9 ya que no guardamos timestamps exactos de hitos en campos de tiempo)
        # En producción se usaría la diferencia entre IN_ROUTE y COMPLETED

        # 2. Total Entregas
        total = DeliveryService.objects.filter(provider_id=provider_id, status=DeliveryService.Status.ENTREGADO).count()
        IndicadorLogistico.objects.create(provider_id=provider_id, nombre="Entregas Exitosas", valor=total, periodo=periodo)

        # 3. Costo Logístico (Suma de comisiones)
        costo = DeliveryService.objects.filter(provider_id=provider_id, status=DeliveryService.Status.ENTREGADO).aggregate(s=Sum('comision_repartidor'))['s'] or 0
        IndicadorLogistico.objects.create(provider_id=provider_id, nombre="Costo Logístico Total", valor=costo, periodo=periodo)

        return True

# Alias para retrocompatibilidad
LogisticService = DeliveryLogisticService
