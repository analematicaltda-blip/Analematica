# backend/stress_test_delivery.py
import os
import django
import time
from concurrent.futures import ThreadPoolExecutor

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')
django.setup()

from api.models import CustomUser
from apps.delivery.models import DeliveryService, Vehicle, Driver
from apps.delivery.services import LogisticService
from apps.companies.models import Company

def simulate_delivery_request(user, payload):
    service = LogisticService(user)
    try:
        req = service.create_request(payload)
        return "SUCCESS"
    except Exception as e:
        return str(e)

def run_delivery_stress_test(num_requests=50):
    print(f"🚀 INICIANDO PRUEBA DE CARGA DELIVERY - {num_requests} SOLICITUDES")

    admin = CustomUser.objects.filter(is_superuser=True).first()
    tourist = CustomUser.objects.filter(role="TURISTA").first()
    company = Company.objects.first()

    payload = {
        "origin_address": "Calle Falsa 123",
        "destination_address": "Avenida Siempre Viva 742",
        "estimated_price": 5000,
        "company_id": str(company.id)
    }

    start_time = time.time()
    results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(simulate_delivery_request, tourist, payload) for _ in range(num_requests)]
        for f in futures:
            results.append(f.result())

    end_time = time.time()

    success_count = results.count("SUCCESS")
    print(f"\n📊 RESULTADOS DELIVERY:")
    print(f"✅ Éxitos: {success_count}")
    print(f"❌ Errores: {num_requests - success_count}")

    total_services = DeliveryService.objects.count()
    print(f"📂 Total servicios en DB: {total_services}")

    if success_count > 0:
        print(f"⏱️ Promedio: {(end_time - start_time)/success_count:.4f}s per request")

if __name__ == "__main__":
    run_delivery_stress_test()
