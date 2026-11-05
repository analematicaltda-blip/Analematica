import os
import django
from decimal import Decimal
from datetime import date

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')
django.setup()

from api.models import CustomUser
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import ProviderProfile
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.models import AsientoContable, Transaccion
from apps.prestadores.mi_negocio.gestion_financiera.models import CuentaBancaria

def verify():
    print("--- Iniciando Verificación Phase C+ ---")

    # 1. Verificar Usuario y Perfil
    prestador = CustomUser.objects.filter(email='prestador@test.com').first()
    if not prestador:
        print("FAIL: Usuario prestador no encontrado.")
        return

    perfil = ProviderProfile.objects.filter(usuario=prestador).first()
    if not perfil:
        print("FAIL: Perfil de prestador no encontrado.")
        return
    print(f"PASS: Perfil '{perfil.nombre_comercial}' verificado.")

    # 2. Verificar Contabilidad
    asientos = AsientoContable.objects.filter(provider=perfil)
    if not asientos.exists():
        print("FAIL: No se encontraron asientos contables para el prestador.")
        return

    asiento = asientos.first()
    print(f"PASS: Asiento '{asiento.descripcion}' encontrado.")

    transacciones = Transaccion.objects.filter(asiento=asiento)
    total_debito = sum(t.debito for t in transacciones)
    total_credito = sum(t.credito for t in transacciones)

    if total_debito != total_credito:
        print(f"FAIL: Asiento descuadrado. Debito: {total_debito}, Credito: {total_credito}")
    else:
        print(f"PASS: Partida doble verificada. Total: ${total_debito}")

    # 3. Verificar Finanzas
    cta = CuentaBancaria.objects.filter(perfil_ref_id=perfil.id).first()
    if not cta:
        print("FAIL: Cuenta bancaria no encontrada.")
    else:
        print(f"PASS: Cuenta bancaria en '{cta.banco}' verificada. Saldo Actual: ${cta.saldo_actual}")

    # 4. Verificar SuperAdmin
    admin = CustomUser.objects.filter(is_superuser=True).first()
    if admin:
        print(f"PASS: SuperAdmin '{admin.email}' activo.")

    print("--- Verificación E2E Exitosa ---")

if __name__ == "__main__":
    verify()
