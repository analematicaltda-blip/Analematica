from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction, models
from django.utils import timezone
from .models import (
    Empleado, Contrato, Planilla, DetalleLiquidacion,
    NovedadNomina, IncapacidadLaboral, ProvisionNomina, IndicadorLaboral
)
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import ProviderProfile
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.models import AsientoContable, Transaccion, Cuenta, PeriodoContable
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.services import ContabilidadService

class NormativaNomina:
    """
    Parámetros de Ley Colombiana 2024/2025.
    """
    SMMLV = Decimal('1300000.00')
    AUX_TRANSPORTE = Decimal('162000.00')
    SALUD_EMPLEADO = Decimal('0.04')
    PENSION_EMPLEADO = Decimal('0.04')
    SALUD_PATRON = Decimal('0.085')
    PENSION_PATRON = Decimal('0.12')
    ARL_CLASE_1 = Decimal('0.00522')
    PRIMA_PROVISION = Decimal('0.0833')
    CESANTIAS_PROVISION = Decimal('0.0833')
    INT_CESANTIAS_PROVISION = Decimal('0.12') # 12% anual sobre cesantías
    VACACIONES_PROVISION = Decimal('0.0417')
    CAJA_COMPENSACION = Decimal('0.04')

class NominaService:
    """
    Motor Central de Nómina SARITA.
    Maneja liquidación, provisiones e integración contable.
    """

    @staticmethod
    @transaction.atomic
    def liquidar_periodo(planilla_id, usuario_id=None):
        planilla = Planilla.objects.select_for_update().get(id=planilla_id)

        # 1. Blindaje de Estado
        if planilla.estado != Planilla.EstadoPlanilla.BORRADOR:
            raise ValueError(f"Blindaje Activo: La planilla {planilla_id} ya fue liquidada/cerrada.")

        # 2. Blindaje de Periodo Contable
        periodo = PeriodoContable.objects.filter(
            provider=planilla.perfil,
            fecha_inicio__lte=planilla.periodo_inicio,
            fecha_fin__gte=planilla.periodo_fin,
            cerrado=False
        ).first()
        if not periodo:
            raise ValueError("Acción Bloqueada: No existe un período contable abierto para estas fechas.")

        # Limpiar liquidaciones previas si existen
        planilla.detalles_liquidacion.all().delete()

        empleados = Empleado.objects.filter(perfil=planilla.perfil, estado=Empleado.EstadoEmpleado.ACTIVO)

        total_dev = Decimal('0.00')
        total_ded = Decimal('0.00')

        for emp in empleados:
            contrato = emp.contratos.filter(activo=True).first()
            if not contrato: continue

            # 1. Validación de Entradas e IBC (Ingreso Base de Cotización)
            salario_base = contrato.salario
            # Días reales trabajados (Descontando ausencias no justificadas e incapacidades)
            # Simplificado para esta fase, pero ya no es un 30 estático.
            ausencias_dias = Ausencia.objects.filter(empleado=emp, justificada=False).count() # Placeholder dias
            dias = 30 - ausencias_dias

            basico_proporcional = (salario_base / Decimal('30')) * Decimal(dias)

            # 2. Devengados Determinísticos
            aux_transporte = NormativaNomina.AUX_TRANSPORTE if salario_base <= (NormativaNomina.SMMLV * 2) else Decimal('0.00')
            if dias < 30:
                aux_transporte = (aux_transporte / Decimal('30')) * Decimal(dias)

            novedades = NovedadNomina.objects.filter(empleado=emp, planilla=planilla, procesada=False)
            extra_dev = sum(n.valor for n in novedades if n.concepto.tipo == 'DEVENGADO')
            extra_ded = sum(n.valor for n in novedades if n.concepto.tipo == 'DEDUCCION')

            total_emp_dev = basico_proporcional + aux_transporte + extra_dev

            # 3. Deducciones Reales (Salud 4%, Pensión 4%)
            ibc = total_emp_dev - aux_transporte # Simplificación IBC
            salud = (ibc * NormativaNomina.SALUD_EMPLEADO).quantize(Decimal('1.'), rounding=ROUND_HALF_UP)
            pension = (ibc * NormativaNomina.PENSION_EMPLEADO).quantize(Decimal('1.'), rounding=ROUND_HALF_UP)

            total_emp_ded = salud + pension + extra_ded
            neto = total_emp_dev - total_emp_ded

            # 4. Prestaciones Sociales (Causación Determinística)
            # La base de prima y cesantías incluye el auxilio de transporte
            prima = (total_emp_dev * NormativaNomina.PRIMA_PROVISION).quantize(Decimal('1.'), rounding=ROUND_HALF_UP)
            cesantias = (total_emp_dev * NormativaNomina.CESANTIAS_PROVISION).quantize(Decimal('1.'), rounding=ROUND_HALF_UP)
            int_cesantias = (cesantias * NormativaNomina.INT_CESANTIAS_PROVISION).quantize(Decimal('1.'), rounding=ROUND_HALF_UP)
            vacaciones = (basico_proporcional * NormativaNomina.VACACIONES_PROVISION).quantize(Decimal('1.'), rounding=ROUND_HALF_UP)

            # 5. Aportes Patronales (Carga Prestacional)
            # Nota: Muchas empresas están exentas de salud patronal si tienen <10 empleados
            salud_patron = (ibc * NormativaNomina.SALUD_PATRON).quantize(Decimal('1.'), rounding=ROUND_HALF_UP)
            pension_patron = (ibc * NormativaNomina.PENSION_PATRON).quantize(Decimal('1.'), rounding=ROUND_HALF_UP)
            arl = (ibc * NormativaNomina.ARL_CLASE_1).quantize(Decimal('1.'), rounding=ROUND_HALF_UP)

            detalle = DetalleLiquidacion.objects.create(
                planilla=planilla,
                empleado=emp,
                salario_base=salario_base,
                dias_trabajados=dias,
                basico=basico_proporcional,
                auxilio_transporte=aux_transporte,
                total_devengado=total_emp_dev,
                salud_empleado=salud,
                pension_empleado=pension,
                total_deduccion=total_emp_ded,
                total_neto=neto,
                valor_prima=prima,
                valor_cesantias=cesantias,
                valor_intereses_cesantias=int_cesantias,
                valor_vacaciones=vacaciones,
                valor_aporte_salud_patron=salud_patron,
                valor_aporte_pension_patron=pension_patron,
                valor_aporte_arl=arl
            )

            total_dev += total_emp_dev
            total_ded += total_emp_ded

            # Marcar novedades como procesadas
            novedades.update(procesada=True)

        planilla.total_devengado = total_dev
        planilla.total_deduccion = total_ded
        planilla.total_neto = total_dev - total_ded
        planilla.estado = Planilla.EstadoPlanilla.LIQUIDADA
        planilla.save()

        # 6. Emisión de Evento de Omnisciencia (Fase 4)
        from apps.core_erp.event_bus import EventBus
        EventBus.emit(
            "PAYROLL_LIQUIDATED_V2",
            {
                "entity_id": str(planilla.perfil.id),
                "planilla_id": str(planilla.id),
                "total_neto": float(planilla.total_neto),
                "periodo": f"{planilla.periodo_inicio} - {planilla.periodo_fin}"
            },
            severity="info"
        )

        return planilla

    @staticmethod
    @transaction.atomic
    def contabilizar_nomina(planilla_id, usuario_id=None):
        planilla = Planilla.objects.select_for_update().get(id=planilla_id)

        # 1. Idempotencia: Evitar duplicidad de asientos
        if planilla.asiento_contable_ref_id:
            raise ValueError(f"Idempotencia Activa: La planilla {planilla_id} ya tiene un asiento contable (Ref: {planilla.asiento_contable_ref_id}).")

        if planilla.estado != Planilla.EstadoPlanilla.LIQUIDADA:
            raise ValueError("Solo se pueden contabilizar planillas en estado LIQUIDADA.")

        # Buscar periodo contable
        periodo = PeriodoContable.objects.filter(
            provider=planilla.perfil,
            fecha_inicio__lte=planilla.periodo_inicio,
            fecha_fin__gte=planilla.periodo_fin,
            cerrado=False
        ).first()

        if not periodo:
            raise ValueError("No existe un período contable abierto para las fechas de la planilla.")

        # Crear Asiento
        asiento = AsientoContable.objects.create(
            provider=planilla.perfil,
            periodo=periodo,
            fecha=timezone.now().date(),
            descripcion=f"CAUSACION NOMINA PERIODO {planilla.periodo_inicio} - {planilla.periodo_fin}",
            creado_por_id=usuario_id
        )

        # Aquí vendría la lógica de mapeo de cuentas.
        # Para esta fase structural, buscaremos o crearemos cuentas por defecto.
        # En una implementación real, esto lo define el Plan de Cuentas del Tenant.

        def get_cuenta(codigo, nombre, tipo):
            plan = planilla.perfil.plandecuentas_items.first()
            cuenta, _ = Cuenta.objects.get_or_create(
                plan_de_cuentas=plan,
                codigo=codigo,
                defaults={'nombre': nombre, 'tipo': tipo, 'provider': planilla.perfil}
            )
            return cuenta

        c_gasto_sueldos = get_cuenta("510506", "Sueldos Básicos", "GASTOS")
        c_gasto_transp = get_cuenta("510527", "Auxilio de Transporte", "GASTOS")

        c_pasivo_nomina = get_cuenta("250505", "Salarios por Pagar", "PASIVO")
        c_pasivo_salud = get_cuenta("237005", "Aportes a Salud", "PASIVO")
        c_pasivo_pension = get_cuenta("238030", "Aportes a Pensión", "PASIVO")

        # Cuentas de Provisiones (Pasivos Estimados)
        c_pasivo_prima = get_cuenta("261005", "Provisión Prima de Servicios", "PASIVO")
        c_pasivo_cesantias = get_cuenta("261010", "Provisión Cesantías", "PASIVO")

        detalles = planilla.detalles_liquidacion.all()

        # 1. Registro de Gastos y Devengados (DEBITOS)
        total_basicos = sum(d.basico for d in detalles)
        total_aux_transp = sum(d.auxilio_transporte for d in detalles)

        Transaccion.objects.create(asiento=asiento, cuenta=c_gasto_sueldos, debito=total_basicos, descripcion="Gasto Sueldos")
        if total_aux_transp > 0:
            Transaccion.objects.create(asiento=asiento, cuenta=c_gasto_transp, debito=total_aux_transp, descripcion="Gasto Aux. Transporte")

        # 2. Registro de Deducciones de Empleados (CREDITOS)
        t_salud_emp = sum(d.salud_empleado for d in detalles)
        t_pension_emp = sum(d.pension_empleado for d in detalles)

        Transaccion.objects.create(asiento=asiento, cuenta=c_pasivo_salud, credito=t_salud_emp, descripcion="Deducción Salud Emp.")
        Transaccion.objects.create(asiento=asiento, cuenta=c_pasivo_pension, credito=t_pension_emp, descripcion="Deducción Pensión Emp.")

        # 3. Neto a Pagar (CREDITO)
        Transaccion.objects.create(asiento=asiento, cuenta=c_pasivo_nomina, credito=planilla.total_neto, descripcion="Neto a Pagar Nómina")

        # 4. Causación de Provisiones Sociales (Opcional en causación de nómina, pero recomendado)
        t_prima = sum(d.valor_prima for d in detalles)
        t_cesantias = sum(d.valor_cesantias for d in detalles)

        # El asiento debe balancear matemáticamente: Debitos = Creditos
        # Total Debito = planilla.total_devengado
        # Total Credito = t_salud + t_pension + planilla.total_neto = total_deduccion + neto = total_devengado

        planilla.estado = Planilla.EstadoPlanilla.CONTABILIZADA
        planilla.asiento_contable_ref_id = asiento.id
        planilla.save()

        return asiento

    @staticmethod
    def generar_indicadores(provider_id):
        provider = ProviderProfile.objects.get(id=provider_id)
        # Costo Laboral Total
        total_costo = DetalleLiquidacion.objects.filter(planilla__perfil=provider).aggregate(s=models.Sum('total_devengado'))['s'] or 0

        IndicadorLaboral.objects.create(
            perfil=provider,
            nombre="Costo Laboral Total",
            valor=total_costo,
            periodo=timezone.now().strftime("%Y-%m")
        )
        return True

    @staticmethod
    @transaction.atomic
    def liquidar_contrato(contrato_id, fecha_retiro, motivo, usuario_id=None):
        """
        Realiza la liquidación final de un contrato laboral.
        """
        contrato = Contrato.objects.select_for_update().get(id=contrato_id)
        if not contrato.activo:
            raise ValueError("El contrato ya está liquidado/inactivo.")

        # Marcar contrato como inactivo
        contrato.fecha_fin = fecha_retiro
        contrato.activo = False
        contrato.save()

        # Actualizar estado del empleado
        empleado = contrato.empleado
        empleado.estado = Empleado.EstadoEmpleado.RETIRADO
        empleado.save()

        # En una implementación real, se generaría un Asiento Contable por el pago de prestaciones.
        return True
