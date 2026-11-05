# backend/sabotage_test_night_11.py
import os
import django
from decimal import Decimal
from django.utils import timezone

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')
django.setup()

from api.models import CustomUser
from apps.prestadores.mi_negocio.operativa_turistica.operadores_directos.bares_discotecas.models import (
    NightEvent, NightConsumption, LiquorInventory
)
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.productos_servicios.models import Product
from apps.admin_plataforma.services.governance_kernel import GovernanceKernel

def run_sabotage_test_night():
    print("🕵️ INICIANDO PRUEBA DE RUPTURA - OPERACIÓN NOCTURNA FASE 11.3")

    provider_user = CustomUser.objects.filter(username="bar_owner").first()
    kernel = GovernanceKernel(provider_user)

    # 1. Intento de Fraude Inventario (Descontar más de lo que hay)
    print("\n--- INTENTO 1: Fraude Inventario (Stock Negativo) ---")
    p = Product.objects.filter(provider__usuario=provider_user).first()
    liquor = LiquorInventory.objects.get(product=p)
    liquor.stock_actual = 5
    liquor.save()

    c = NightConsumption.objects.filter(estado="ABIERTO").first()
    if not c:
        event = NightEvent.objects.first()
        c = NightConsumption.objects.create(provider=event.provider, evento=event, staff_responsable=provider_user)

    try:
        kernel.resolve_and_execute("PROCESS_COMMAND", {
            "consumption_id": str(c.id),
            "items": [{"product_id": p.id, "cantidad": 10}], # Pide 10 habiendo 5
            "user_id": provider_user.id
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"✅ BLOQUEO EXITOSO (STOCK INSUFICIENTE): {e}")

    # 2. Manipulación de Cierre (Cerrar con consumos abiertos)
    # En esta implementación, el cierre de caja calcula sobre lo facturado.
    # Pero una regla de negocio superior debería impedir el cierre si hay consumos abiertos.

    # 3. Doble Facturación (Simulada por Idempotencia del orquestador si se usa la misma misión,
    # pero aquí probamos la lógica del servicio)
    print("\n--- INTENTO 2: Doble Facturación del mismo consumo ---")
    try:
        kernel.resolve_and_execute("BILL_CONSUMPTION", {"consumption_id": str(c.id), "user_id": provider_user.id})
        # Segundo intento
        kernel.resolve_and_execute("BILL_CONSUMPTION", {"consumption_id": str(c.id), "user_id": provider_user.id})
    except Exception as e:
        print(f"✅ BLOQUEO EXITOSO (YA FACTURADO): {e}")

    print("\n🏁 PRUEBA DE RUPTURA NOCTURNA FINALIZADA.")

if __name__ == "__main__":
    run_sabotage_test_night()
