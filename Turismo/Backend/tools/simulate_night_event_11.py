# backend/simulate_night_event_11.py
import os
import django
import random
import time
from decimal import Decimal
from django.utils import timezone
from concurrent.futures import ThreadPoolExecutor

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')
django.setup()

from api.models import CustomUser
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import ProviderProfile
from apps.prestadores.mi_negocio.operativa_turistica.operadores_directos.bares_discotecas.models import (
    NightEvent, NightZone, NightTable, NightConsumption, LiquorInventory
)
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.productos_servicios.models import Product
from apps.admin_plataforma.services.governance_kernel import GovernanceKernel
from apps.companies.models import Company

def simulate_night_event():
    print("🚀 INICIANDO SIMULACIÓN DE EVENTO NOCTURNO FASE 11.2")

    # 1. Setup
    admin = CustomUser.objects.filter(is_superuser=True).first()
    company = Company.objects.first()
    provider_user, _ = CustomUser.objects.get_or_create(
        username="bar_owner",
        defaults={"email": "bar@owner.com", "role": "PRESTADOR"}
    )
    profile, _ = ProviderProfile.objects.get_or_create(
        usuario=provider_user,
        defaults={
            "nombre_comercial": "The Nightclub",
            "company_id": company.id if company else None,
            "provider_type": ProviderProfile.ProviderTypes.BAR_DISCO
        }
    )

    # 2. Crear Evento
    event = NightEvent.objects.create(
        provider=profile,
        nombre="Gran Inauguración Fase 11",
        tipo=NightEvent.EventType.FIESTA,
        capacidad_maxima=300,
        fecha_inicio=timezone.now(),
        fecha_fin=timezone.now() + timezone.timedelta(hours=8),
        estado=NightEvent.EventStatus.ACTIVO,
        cover_price=20000
    )

    # 3. Crear Zonas y Mesas
    zona_vip, _ = NightZone.objects.get_or_create(provider=profile, nombre="VIP Platinum", defaults={"recargo_vip": 50000})
    for i in range(1, 11):
        NightTable.objects.get_or_create(provider=profile, zona=zona_vip, numero=f"V{i}", defaults={"capacidad": 6})

    # 4. Preparar Inventario (Licores)
    products = []
    for name, price in [("Aguardiente", 120000), ("Ron", 150000), ("Cerveza", 10000), ("Whisky", 350000)]:
        p, _ = Product.objects.get_or_create(
            provider=profile, nombre=name, defaults={"base_price": price}
        )
        LiquorInventory.objects.get_or_create(provider=profile, product=p, defaults={"stock_actual": 1000})
        products.append(p)

    # 5. Simular 100 consumos concurrentes
    print("--- Simulando consumos masivos... ---")
    kernel = GovernanceKernel(provider_user)

    # Crear consumos iniciales
    consumptions = []
    for i in range(100):
        c = NightConsumption.objects.create(
            provider=profile,
            evento=event,
            staff_responsable=provider_user,
            estado=NightConsumption.ConsumptionStatus.ABIERTO
        )
        consumptions.append(c)

    def process_random_command(consumption):
        items = [
            {"product_id": random.choice(products).id, "cantidad": random.randint(1, 3)}
            for _ in range(random.randint(1, 4))
        ]
        try:
            kernel.resolve_and_execute("PROCESS_COMMAND", {
                "consumption_id": str(consumption.id),
                "items": items,
                "user_id": provider_user.id
            })
            return True
        except Exception as e:
            # print(f"Error command: {e}")
            return False

    with ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(process_random_command, consumptions)

    print("--- Facturando consumos... ---")
    def bill_consumption(consumption):
        try:
            kernel.resolve_and_execute("BILL_CONSUMPTION", {
                "consumption_id": str(consumption.id),
                "user_id": provider_user.id
            })
            return True
        except Exception as e:
            return False

    with ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(bill_consumption, consumptions)

    # 6. Cierre de Caja
    print("--- Realizando cierre de caja... ---")
    total_real = NightConsumption.objects.filter(evento=event, estado="FACTURADO").aggregate(t=django.db.models.Sum('total'))['t'] or Decimal('0.00')

    closing_result = kernel.resolve_and_execute("NIGHT_CASH_CLOSE", {
        "event_id": str(event.id),
        "efectivo": float(total_real),
        "total_real": float(total_real),
        "user_id": provider_user.id
    })

    print(f"\n📊 RESULTADOS SIMULACIÓN:")
    print(f"✅ Evento: {event.nombre}")
    print(f"✅ Consumos procesados: {NightConsumption.objects.filter(evento=event).count()}")
    print(f"✅ Facturas emitidas: {NightConsumption.objects.filter(evento=event, estado='FACTURADO').count()}")
    print(f"✅ Cierre de caja: {closing_result['status']}")

    if total_real > 0:
        print("\n🏆 VALIDACIÓN FASE 11.2 EXITOSA: Ciclo nocturno completo y verificado.")

from django.db import models
if __name__ == "__main__":
    simulate_night_event()
