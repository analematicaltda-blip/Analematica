from django.core.management.base import BaseCommand
from apps.core_erp.accounting.models import Account, ChartOfAccounts
from apps.core_erp.tenancy.models import Tenant
from django.db import transaction

class Command(BaseCommand):
    help = 'Carga el Catálogo de Cuentas (PUC) de Colombia para un tenant específico'

    def add_arguments(self, parser):
        parser.add_argument('tenant_id', type=str, help='ID del tenant para cargar las cuentas')

    def handle(self, *args, **options):
        tenant_id = options['tenant_id']
        try:
            tenant = Tenant.objects.get(id=tenant_id)
        except Tenant.DoesNotExist:
            self.stderr.write(f"Tenant {tenant_id} no encontrado")
            return

        puc_data = [
            ("1", "ACTIVO"),
            ("11", "DISPONIBLE"),
            ("1105", "CAJA"),
            ("110505", "CAJA GENERAL"),
            ("110510", "CAJAS MENORES"),
            ("110515", "MONEDA EXTRANJERA"),
            ("1110", "BANCOS"),
            ("111005", "MONEDA NACIONAL"),
            ("111010", "MONEDA EXTRANJERA"),
            ("1115", "REMESAS EN TRANSITO"),
            ("111505", "MONEDA NACIONAL"),
            ("111510", "MONEDA EXTRANJERA"),
            ("1120", "CUENTAS DE AHORRO"),
            ("112005", "BANCOS"),
            ("112010", "CORPORACIONES DE AHORRO Y VIVIENDA"),
            ("112015", "ORGANISMOS COOPERATIVOS FINANCIEROS"),
            ("1125", "FONDOS"),
            ("112505", "ROTATORIOS MONEDA NACIONAL"),
            ("12", "INVERSIONES"),
            ("1205", "ACCIONES"),
            ("1210", "CUOTAS O PARTES DE INTERES SOCIAL"),
            ("13", "DEUDORES"),
            ("1305", "CLIENTES"),
            ("130505", "NACIONALES"),
            ("14", "INVENTARIOS"),
            ("1435", "MERCANCIAS NO FABRICADAS POR LA EMPRESA"),
            ("15", "PROPIEDADES PLANTA Y EQUIPO"),
            ("1516", "CONSTRUCCIONES Y EDIFICACIONES"),
            ("1524", "EQUIPO DE OFICINA"),
            ("1540", "FLOTA Y EQUIPO DE TRANSPORTE"),
            ("2", "PASIVO"),
            ("21", "OBLIGACIONES FINANCIERAS"),
            ("22", "PROVEEDORES"),
            ("23", "CUENTAS POR PAGAR"),
            ("24", "IMPUESTOS, GRAVAMENES Y TASAS"),
            ("3", "PATRIMONIO"),
            ("31", "CAPITAL SOCIAL"),
            ("4", "INGRESOS"),
            ("41", "OPERACIONALES"),
            ("4135", "COMERCIO AL POR MAYOR Y AL POR MENOR"),
            ("5", "GASTOS"),
            ("51", "OPERACIONALES DE ADMINISTRACION"),
            ("5105", "GASTOS DE PERSONAL"),
            ("52", "OPERACIONALES DE VENTAS"),
            ("6", "COSTOS DE VENTAS"),
            ("7", "COSTOS DE PRODUCCION O DE OPERACION"),
            ("8", "CUENTAS DE ORDEN DEUDORAS"),
            ("9", "CUENTAS DE ORDEN ACREEDORAS"),
        ]

        with transaction.atomic():
            chart, _ = ChartOfAccounts.objects.get_or_create(
                tenant=tenant,
                name="PUC Colombia",
                defaults={"description": "Plan Único de Cuentas para Colombia"}
            )

            type_map = {
                '1': 'ASSET',
                '2': 'LIABILITY',
                '3': 'EQUITY',
                '4': 'REVENUE',
                '5': 'EXPENSE',
                '6': 'COST_OF_SALES',
                '7': 'PRODUCTION_COST',
                '8': 'DEBTOR_ORDER',
                '9': 'CREDITOR_ORDER',
            }

            for code, name in puc_data:
                clase = code[0]
                acc_type = type_map.get(clase)

                # Buscar padre basándonos en la longitud del código
                parent = None
                if len(code) > 1:
                    # Lógica simple: el padre tiene una longitud menor y es un prefijo
                    potential_parents = [code[:l] for l in [1, 2, 4, 6] if l < len(code)]
                    if potential_parents:
                        parent_code = potential_parents[-1]
                        parent = Account.objects.filter(code=parent_code, tenant=tenant).first()

                Account.objects.update_or_create(
                    tenant=tenant,
                    chart_of_accounts=chart,
                    code=code,
                    defaults={
                        "name": name,
                        "type": acc_type,
                        "parent_account": parent,
                        "is_active": True
                    }
                )

        self.stdout.write(self.style.SUCCESS(f'PUC cargado exitosamente para el tenant {tenant_id}'))
