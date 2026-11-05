# backend/stress_test_erp_sales.py
import os
import django
import time
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')
django.setup()

from api.models import CustomUser
from apps.prestadores.mi_negocio.gestion_comercial.domain.models import OperacionComercial
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.models import AsientoContable, Transaccion, PeriodoContable, Cuenta
from apps.admin_plataforma.services.quintuple_erp import QuintupleERPService
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import ProviderProfile
from apps.companies.models import Company

def simulate_sale(user, profile_id, client_id, company_id, amount):
    erp_service = QuintupleERPService(user)
    payload = {
        "perfil_id": profile_id,
        "cliente_id": client_id,
        "company_id": company_id,
        "amount": amount,
        "description": "Stress Sale"
    }
    try:
        result = erp_service.record_impact("SALE", payload)
        return "SUCCESS"
    except Exception as e:
        return str(e)

def run_erp_stress_test(num_threads=5, sales_per_thread=10):
    print(f"🚀 INICIANDO PRUEBA DE RUPTURA ERP - {num_threads * sales_per_thread} VENTAS")

    admin = CustomUser.objects.filter(is_superuser=True).first()
    company = Company.objects.first()

    # Asegurar Perfil y Cliente
    import uuid
    client_id = uuid.uuid4()

    # Crear un ProviderProfile real
    from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import ProviderProfile
    provider_user, _ = CustomUser.objects.get_or_create(username="erp_tester", defaults={"email": "erp@test.com", "role": "PRESTADOR"})
    profile, _ = ProviderProfile.objects.get_or_create(
        usuario=provider_user,
        defaults={
            "nombre_comercial": "Stress Test Corp",
            "company_id": company.id,
            "provider_type": ProviderProfile.ProviderTypes.HOTEL
        }
    )
    profile_id = profile.id

    # Crear Periodo Contable para que el impact_contable no falle
    PeriodoContable.objects.get_or_create(
        provider=profile,
        cerrado=False,
        defaults={
            "nombre": "Test Stress",
            "fecha_inicio": "2026-01-01",
            "fecha_fin": "2026-12-31"
        }
    )

    start_time = time.time()
    results = []

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(simulate_sale, admin, profile_id, client_id, company.id, 100) for _ in range(num_threads * sales_per_thread)]
        for f in futures:
            results.append(f.result())

    end_time = time.time()

    success_count = results.count("SUCCESS")
    print(f"\n📊 RESULTADOS ERP:")
    print(f"✅ Éxitos: {success_count}")
    print(f"❌ Errores: {len(results) - success_count}")

    # Verificar consistencia en DB
    total_asientos = AsientoContable.objects.filter(provider_id=profile_id).count()
    total_operaciones = OperacionComercial.objects.filter(perfil_ref_id=profile_id).count()

    print(f"📂 Asientos creados: {total_asientos}")
    print(f"📂 Operaciones comerciales: {total_operaciones}")

    if success_count == total_asientos == total_operaciones:
        print("\n🏆 INTEGRIDAD ERP MANTENIDA.")
    else:
        print("\n⚠️ DESCUADRE DETECTADO ENTRE DIMENSIONES ERP.")

if __name__ == "__main__":
    run_erp_stress_test()
