# backend/simulate_transport_13.py
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
from apps.prestadores.mi_negocio.operativa_turistica.operadores_directos.transporte.models import (
    Vehicle, Conductor, TransportRoute, ScheduledTrip, TransportBooking
)
from apps.admin_plataforma.services.governance_kernel import GovernanceKernel
from apps.companies.models import Company

def simulate_transport():
    print("🚀 INICIANDO SIMULACIÓN DE TRANSPORTE TURÍSTICO FASE 13.2")

    # 0. Limpieza previa
    print("--- Limpiando datos previos... ---")
    TransportBooking.objects.all().delete()
    ScheduledTrip.objects.all().delete()
    Conductor.objects.all().delete()
    Vehicle.objects.all().delete()
    TransportRoute.objects.all().delete()

    print(f"DEBUG: Conteo tras limpieza: ScheduledTrip={ScheduledTrip.objects.count()}")

    # 1. Setup
    company, _ = Company.objects.get_or_create(name="TransportPG", defaults={"code": "TPG"})
    provider_user, _ = CustomUser.objects.get_or_create(username="transport_owner", defaults={"role":"PRESTADOR", "email":"transport@test.com"})
    profile, _ = ProviderProfile.objects.get_or_create(
        usuario=provider_user,
        defaults={"nombre_comercial": "Transportes PG", "provider_type":"TRANSPORT", "is_active": True}
    )

    # 2. Crear Vehículos
    print("--- Creando flota de vehículos... ---")
    vehicles = []
    for i in range(1, 4):
        v, _ = Vehicle.objects.get_or_create(
            provider=profile,
            placa=f"TRS-00{i}",
            defaults={"tipo": "Van Turística", "capacidad_maxima": 15, "status": "AVAILABLE"}
        )
        vehicles.append(v)

    # 3. Crear Conductores
    print("--- Creando conductores... ---")
    conductors = []
    for i in range(1, 4):
        u, _ = CustomUser.objects.get_or_create(
            username=f"driver_{i}",
            defaults={"email": f"driver{i}@test.com", "role": "PRESTADOR"}
        )
        c, _ = Conductor.objects.get_or_create(
            provider=profile,
            usuario=u,
            defaults={
                "licencia_conduccion": f"LIC-TR-{i}",
                "categoria_licencia": "C2",
                "fecha_vencimiento_licencia": timezone.now().date() + timezone.timedelta(days=365)
            }
        )
        conductors.append(c)

    # 4. Crear Rutas
    ruta_pg, _ = TransportRoute.objects.get_or_create(
        provider=profile,
        nombre="Puerto Gaitán - Mirador",
        defaults={"origen": "Centro", "destino": "Mirador", "distancia_km": 15, "precio_base": 25000}
    )

    # 5. Programar Viajes
    print("--- Programando viajes... ---")
    kernel = GovernanceKernel(provider_user)

    trips = []
    for i in range(1, 4): # 3 vehicles, 3 trips at different times
        hora = (timezone.now() + timezone.timedelta(hours=i)).time()
        # Usar Kernel para programar (Fase 13.1)
        res = kernel.resolve_and_execute("SCHEDULE_TRANSPORT_TRIP", {
            "ruta_id": str(ruta_pg.id),
            "fecha_salida": str(timezone.now().date()),
            "hora_salida": str(hora),
            "vehiculo_id": str(vehicles[i-1].id), # Ensure different vehicle
            "conductor_id": str(conductors[i-1].id), # Ensure different conductor
            "capacidad_total": 15,
            "precio_por_pasajero": 25000,
            "user_id": provider_user.id,
            "action": "SCHEDULE_TRANSPORT_TRIP"
        })
        trips.append(res['trip_id'])

    # 6. Simular Reservas masivas (Overbooking Check)
    print("--- Registrando reservas masivas... ---")
    import uuid
    client_id = uuid.uuid4()

    trip_id = trips[0]
    success_bookings = 0
    failed_bookings = 0

    for _ in range(20): # Intentar 20 reservas de 1 persona en una van de 15
        try:
            kernel.resolve_and_execute("BOOK_TRANSPORT_SEAT", {
                "trip_id": trip_id,
                "cliente_ref_id": str(client_id),
                "numero_pasajeros": 1,
                "user_id": provider_user.id,
                "action": "BOOK_TRANSPORT_SEAT"
            })
            success_bookings += 1
        except Exception as e:
            # print(f"Reserva fallida (esperado): {e}")
            failed_bookings += 1

    print(f"\n📊 RESULTADOS SIMULACIÓN TRANSPORTE:")
    print(f"✅ Viajes programados: {len(trips)}")
    print(f"✅ Reservas exitosas: {success_bookings}")
    print(f"✅ Intentos bloqueados (Overbooking): {failed_bookings}")

    if success_bookings == 15 and failed_bookings == 5:
        print("\n🏆 VALIDACIÓN FASE 13.2 EXITOSA: Control de capacidad impecable.")

if __name__ == "__main__":
    simulate_transport()
