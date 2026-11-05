# backend/sabotage_test_transport_13.py
import os
import django
from django.utils import timezone
from datetime import timedelta, date, time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')
django.setup()

from api.models import CustomUser
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import ProviderProfile
from apps.prestadores.mi_negocio.operativa_turistica.operadores_directos.transporte.models import Vehicle, Conductor, TransportRoute, ScheduledTrip
from apps.admin_plataforma.services.governance_kernel import GovernanceKernel

def run_sabotage_test():
    print("⚔️ INICIANDO PRUEBAS DE SABOTAJE FASE 13.3 - TRANSPORTE")

    user = CustomUser.objects.filter(username="transport_owner").first()
    profile = ProviderProfile.objects.filter(usuario=user).first()
    kernel = GovernanceKernel(user)

    # Limpieza
    ScheduledTrip.objects.all().delete()
    Vehicle.objects.all().delete()
    Conductor.objects.all().delete()

    # 1. Sabotaje: Vehículo con documentos vencidos
    print("\n[TEST 1] Intento programar con vehículo vencido...")
    v_vencido = Vehicle.objects.create(
        provider=profile,
        placa="SAB-001",
        insurance_expiry_date=timezone.now().date() - timedelta(days=1),
        status='AVAILABLE',
        capacidad_maxima=10
    )
    c = Conductor.objects.create(
        provider=profile,
        usuario=user,
        licencia_conduccion="SAB-LIC-1",
        fecha_vencimiento_licencia=date(2030, 1, 1)
    )
    r = TransportRoute.objects.filter(provider=profile).first()

    try:
        kernel.resolve_and_execute("SCHEDULE_TRANSPORT_TRIP", {
            "ruta_id": str(r.id),
            "fecha_salida": str(date(2025, 1, 1)),
            "hora_salida": "10:00:00",
            "vehiculo_id": str(v_vencido.id),
            "conductor_id": str(c.id),
            "capacidad_total": 10,
            "precio_por_pasajero": 1000,
            "user_id": user.id,
            "action": "SCHEDULE_TRANSPORT_TRIP"
        })
        print("❌ FALLO: Se permitió programar con vehículo vencido.")
    except Exception as e:
        print(f"✅ ÉXITO: Bloqueado correctamente: {e}")

    # 2. Sabotaje: Solapamiento de Conductor
    print("\n[TEST 2] Intento solapar conductor en mismo horario...")
    v2 = Vehicle.objects.create(provider=profile, placa="SAB-002", insurance_expiry_date=date(2030,1,1))
    v3 = Vehicle.objects.create(provider=profile, placa="SAB-003", insurance_expiry_date=date(2030,1,1))

    # Primer viaje (Exitoso)
    kernel.resolve_and_execute("SCHEDULE_TRANSPORT_TRIP", {
        "ruta_id": str(r.id),
        "fecha_salida": "2025-02-01",
        "hora_salida": "14:00:00",
        "vehiculo_id": str(v2.id),
        "conductor_id": str(c.id),
        "capacidad_total": 10,
        "precio_por_pasajero": 1000,
        "user_id": user.id,
        "action": "SCHEDULE_TRANSPORT_TRIP"
    })

    # Segundo viaje con mismo conductor
    try:
        kernel.resolve_and_execute("SCHEDULE_TRANSPORT_TRIP", {
            "ruta_id": str(r.id),
            "fecha_salida": "2025-02-01",
            "hora_salida": "14:00:00",
            "vehiculo_id": str(v3.id),
            "conductor_id": str(c.id),
            "capacidad_total": 10,
            "precio_por_pasajero": 1000,
            "user_id": user.id,
            "action": "SCHEDULE_TRANSPORT_TRIP"
        })
        print("❌ FALLO: Se permitió solapar al conductor.")
    except Exception as e:
        print(f"✅ ÉXITO: Bloqueado correctamente: {e}")

    # 3. Sabotaje: Liquidación prematura
    print("\n[TEST 3] Intento liquidar un viaje que aún está PROGRAMADO...")
    trip = ScheduledTrip.objects.filter(estado='PROGRAMADO').first()
    try:
        kernel.resolve_and_execute("LIQUIDATE_TRANSPORT_TRIP", {
            "trip_id": str(trip.id),
            "user_id": user.id,
            "action": "LIQUIDATE_TRANSPORT_TRIP"
        })
        print("❌ FALLO: Se permitió liquidar viaje no finalizado.")
    except Exception as e:
        print(f"✅ ÉXITO: Bloqueado correctamente: {e}")

    print("\n🏁 PRUEBAS DE SABOTAJE FINALIZADAS.")

if __name__ == "__main__":
    run_sabotage_test()
