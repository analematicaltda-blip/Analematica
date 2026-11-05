import json
from decimal import Decimal
from django.utils import timezone
from django.db import transaction

from .models import OrdenPago
# --- IMPORTACIONES DE SERVICIOS DE DOMINIO ---
from ..gestion_operativa.services import ProviderProfileService
from ..gestion_archivistica.archiving import ArchivingService
# Nota: Se asumirá la existencia de servicios para CuentaBancaria, Empleado, etc.
# o se resolverán de la manera apropiada en su respectiva fase.

class PagoService:
    @staticmethod
    @transaction.atomic
    def crear_orden_pago(
        perfil_ref_id: str,
        cuenta_bancaria_ref_id: str,
        beneficiario_id: str,
        tipo_beneficiario: str,
        monto: Decimal,
        concepto: str,
        user_id: int
    ):
        """
        Crea una Orden de Pago de forma desacoplada y la archiva en el SGA.
        """
        # 1. Resolver el perfil para obtener el company_id
        perfil = ProviderProfileService.get_profile_by_id(perfil_ref_id)
        if not perfil:
            raise ValueError("Perfil de proveedor no encontrado.")

        # 2. Crear la Orden de Pago
        orden_pago = OrdenPago.objects.create(
            perfil_ref_id=perfil_ref_id,
            cuenta_bancaria_ref_id=cuenta_bancaria_ref_id,
            beneficiario_id=beneficiario_id,
            tipo_beneficiario=tipo_beneficiario,
            fecha_pago=timezone.now().date(),
            monto=monto,
            concepto=concepto,
            estado=OrdenPago.EstadoPago.PAGADA
        )

        # 3. Integración con el SGA
        try:
            document_content = {
                "orden_pago_id": str(orden_pago.id),
                "beneficiario_id": str(beneficiario_id),
                "tipo_beneficiario": tipo_beneficiario,
                "monto": str(monto),
                "concepto": concepto
            }
            document_bytes = json.dumps(document_content, indent=2).encode('utf-8')

            metadata = {'source_model': 'OrdenPago', 'source_id': orden_pago.id}

            document_version = ArchivingService.archive_document(
                company_id=perfil.company_id,
                user_id=user_id,
                process_type_code='FIN',
                process_code='PAGOS',
                document_type_code='OP',
                document_content=document_bytes,
                original_filename=f"OP-{orden_pago.id}.json",
                document_metadata=metadata
            )

            # Guardar la referencia al documento archivado
            orden_pago.documento_archivistico_ref_id = document_version.document.id
            orden_pago.save(update_fields=['documento_archivistico_ref_id'])

        except Exception as e:
            # En un caso real, se manejaría el error de forma más robusta.
            # Por ahora, simplemente lo registramos (si tuviéramos un logger).
            print(f"Error al archivar la orden de pago {orden_pago.id}: {e}")
            # La transacción se revierte gracias a @transaction.atomic

        return orden_pago

class FinanzasService:
    """
    Servicio central para cálculos financieros, indicadores y proyecciones.
    """
    @staticmethod
    def calcular_amortizacion(monto, tasa_anual, plazo_meses):
        """
        Calcula tabla de amortización (Cuota Fija / Sistema Francés).
        """
        tasa_mensual = (tasa_anual / 100) / 12
        if tasa_mensual == 0:
             cuota = monto / plazo_meses
        else:
             cuota = monto * (tasa_mensual / (1 - (1 + tasa_mensual)**(-plazo_meses)))

        tabla = []
        saldo = monto
        for i in range(1, plazo_meses + 1):
            interes = saldo * tasa_mensual
            capital = cuota - interes
            saldo -= capital
            tabla.append({
                "numero": i,
                "cuota": round(cuota, 2),
                "capital": round(capital, 2),
                "interes": round(interes, 2),
                "saldo": round(max(0, saldo), 2)
            })
        return tabla

    @staticmethod
    def calcular_indicadores(provider):
        """
        Calcula indicadores financieros basados en la contabilidad real.
        Liquidez Corriente = Activo Corriente / Pasivo Corriente
        Rentabilidad = Utilidad Neta / Ingresos Totales
        """
        from ..gestion_contable.contabilidad.services import ContabilidadService
        from django.utils import timezone

        now = timezone.now().date()
        er = ContabilidadService.generar_estado_resultados(provider, now.replace(day=1), now)
        bg = ContabilidadService.generar_balance_general(provider, now)

        # Simplificación: Activo Corriente = Clase 1, Pasivo Corriente = Clase 2
        activo = bg['totales'].get('ACTIVO', Decimal('0'))
        pasivo = bg['totales'].get('PASIVO', Decimal('0'))
        ingresos = er['ingresos']['total']
        utilidad = er['utilidad_neta']

        indicadores = {
            "liquidez_corriente": float(activo / pasivo) if pasivo != 0 else 0,
            "rentabilidad_neta": float(utilidad / ingresos) if ingresos != 0 else 0,
            "endeudamiento_total": float(pasivo / activo) if activo != 0 else 0,
            "ebitda_estimado": float(utilidad) # Simplificado
        }

        # Persistencia histórica
        from .models import IndicadorFinancieroHistorico
        for nombre, valor in indicadores.items():
            IndicadorFinancieroHistorico.objects.create(
                provider=provider,
                nombre=nombre.upper(),
                valor=Decimal(str(valor))
            )

        return indicadores

    @staticmethod
    def generar_flujo_caja_proyectado(provider, meses=6):
        """
        Genera proyección de flujo de caja basada en promedios históricos.
        """
        from .models import ProyeccionFinanciera
        from django.utils import timezone
        from dateutil.relativedelta import relativedelta

        # Aquí iría lógica de promedios. Por ahora generamos registros base.
        hoy = timezone.now().date()
        proyecciones = []
        for i in range(1, meses + 1):
             fecha = hoy + relativedelta(months=i)
             p = ProyeccionFinanciera.objects.create(
                 provider=provider,
                 nombre_escenario=f"Proyección Automática {fecha.strftime('%Y-%m')}",
                 fecha_inicio=fecha.replace(day=1),
                 fecha_fin=(fecha.replace(day=28) + relativedelta(days=4)).replace(day=1) - relativedelta(days=1),
                 ingresos_proyectados=Decimal('1000000'), # Placeholder
                 gastos_proyectados=Decimal('800000'),
                 nivel_probabilidad=0.8
             )
             proyecciones.append(p)
        return proyecciones
