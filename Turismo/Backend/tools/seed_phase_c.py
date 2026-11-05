import os
import django
import uuid
from decimal import Decimal
from datetime import date, timedelta

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')
django.setup()

from api.models import Entity, CustomUser, Department, Municipality
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import CategoriaPrestador, ProviderProfile
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.productos_servicios.models import Product
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.clientes.models import Cliente
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.reservas.models import Reserva
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.models import PlanDeCuentas, Cuenta, PeriodoContable, AsientoContable, Transaccion
from apps.prestadores.mi_negocio.gestion_financiera.models import CuentaBancaria

def seed():
    print("--- Iniciando Seed Phase C+ ---")

    # 1. Crear Entidad Maestras
    meta, _ = Department.objects.get_or_create(id=50, defaults={'name': 'Meta'})
    gaitan, _ = Municipality.objects.get_or_create(id=50313, defaults={'name': 'Puerto Gaitán', 'department': meta})

    entidad, _ = Entity.objects.get_or_create(
        slug='alcaldia-puerto-gaitan',
        defaults={
            'name': 'Alcaldía de Puerto Gaitán',
            'type': 'municipal',
            'primary_color': '#006D5B'
        }
    )

    # 2. Crear Usuarios
    admin_user, created = CustomUser.objects.get_or_create(
        email='admin@sarita.com',
        defaults={
            'username': 'admin@sarita.com',
            'is_staff': True,
            'is_superuser': True,
            'role': CustomUser.Role.ADMIN
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("SuperAdmin creado: admin@sarita.com / admin123")

    prestador_user, created = CustomUser.objects.get_or_create(
        email='prestador@test.com',
        defaults={
            'username': 'prestador@test.com',
            'role': CustomUser.Role.PRESTADOR
        }
    )
    if created:
        prestador_user.set_password('prestador123')
        prestador_user.save()
        print("Prestador creado: prestador@test.com / prestador123")

    # 3. Perfil de Prestador
    cat_hotel, _ = CategoriaPrestador.objects.get_or_create(
        slug='hotel',
        defaults={'nombre': 'Hotel'}
    )

    perfil, _ = ProviderProfile.objects.get_or_create(
        usuario=prestador_user,
        defaults={
            'nombre_comercial': 'Hotel Paraíso Gaitán',
            'provider_type': 'HOTEL',
            'telefono_principal': '3201234567',
            'email_comercial': 'contacto@paraisogaitan.com',
            'direccion': 'Calle 10 # 5-20',
            'is_verified': True
        }
    )
    print(f"Perfil de Prestador verificado: {perfil.nombre_comercial}")

    # 4. Operaciones (Productos y Clientes)
    habitacion, _ = Product.objects.get_or_create(
        provider=perfil,
        nombre='Habitación Suite Real',
        defaults={
            'tipo': 'SERVICIO',
            'base_price': Decimal('250000.00'),
            'descripcion': 'Suite de lujo con vista al río Manacacías'
        }
    )

    cliente, _ = Cliente.objects.get_or_create(
        perfil=perfil,
        email='turista@test.com',
        defaults={
            'nombre': 'Juan Turista',
            'telefono': '3159998877'
        }
    )

    # 5. Contabilidad (Plan de Cuentas)
    plan, _ = PlanDeCuentas.objects.get_or_create(
        provider=perfil,
        nombre='Plan Pymes 2024',
        defaults={'descripcion': 'Plan de cuentas estandarizado para hotelería'}
    )

    # Cuentas base
    activos, _ = Cuenta.objects.get_or_create(
        plan_de_cuentas=plan,
        codigo='1',
        defaults={'nombre': 'Activos', 'tipo': 'ACTIVO', 'provider': perfil}
    )
    caja, _ = Cuenta.objects.get_or_create(
        plan_de_cuentas=plan,
        codigo='1105',
        parent=activos,
        defaults={'nombre': 'Caja General', 'tipo': 'ACTIVO', 'provider': perfil}
    )
    bancos, _ = Cuenta.objects.get_or_create(
        plan_de_cuentas=plan,
        codigo='1110',
        parent=activos,
        defaults={'nombre': 'Bancos', 'tipo': 'ACTIVO', 'provider': perfil}
    )
    ingresos, _ = Cuenta.objects.get_or_create(
        plan_de_cuentas=plan,
        codigo='4',
        defaults={'nombre': 'Ingresos', 'tipo': 'INGRESOS', 'provider': perfil}
    )
    ventas, _ = Cuenta.objects.get_or_create(
        plan_de_cuentas=plan,
        codigo='4135',
        parent=ingresos,
        defaults={'nombre': 'Ventas de Servicios', 'tipo': 'INGRESOS', 'provider': perfil}
    )

    # 6. Período Contable
    hoy = date.today()
    periodo, _ = PeriodoContable.objects.get_or_create(
        provider=perfil,
        fecha_inicio=hoy.replace(day=1),
        fecha_fin=(hoy.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1),
        defaults={'nombre': f'Período {hoy.strftime("%B %Y")}'}
    )

    # 7. Finanzas (Cuenta Bancaria)
    cta_bancaria, _ = CuentaBancaria.objects.get_or_create(
        numero_cuenta='123456789',
        defaults={
            'perfil_ref_id': perfil.id,
            'banco': 'Banco de Bogotá',
            'tipo_cuenta': 'Ahorros',
            'saldo_inicial': Decimal('1000000.00'),
            'saldo_actual': Decimal('1000000.00'),
            'cuenta_contable_ref_id': bancos.id
        }
    )

    # 8. Simulación de una Venta (E2E)
    asiento = AsientoContable.objects.create(
        provider=perfil,
        periodo=periodo,
        fecha=hoy,
        descripcion=f'Venta de Habitación a {cliente.nombre}',
        creado_por=prestador_user
    )

    # Registro de la transacción (Partida Doble)
    # Entra dinero a Bancos (Débito)
    Transaccion.objects.create(
        asiento=asiento,
        cuenta=bancos,
        debito=Decimal('250000.00'),
        descripcion='Recaudo venta suite'
    )
    # Sale de Ventas (Crédito)
    Transaccion.objects.create(
        asiento=asiento,
        cuenta=ventas,
        credito=Decimal('250000.00'),
        descripcion='Ingreso por servicio hotelero'
    )

    print(f"--- Simulación E2E Exitosa: Asiento #{asiento.id} registrado ---")
    print("--- Seed Phase C+ Completado con éxito ---")

if __name__ == "__main__":
    seed()
