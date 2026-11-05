import os
import django
import uuid
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')
django.setup()

from api.models import CustomUser, Artesano, RubroArtesano
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import ProviderProfile
from apps.prestadores.mi_negocio.operativa_turistica.cadena_productiva.artesanos.models import RawMaterial, WorkshopOrder
from apps.sarita_agents.orchestrator import sarita_orchestrator

def simulate_artisan_production():
    print("Iniciando simulación de producción artesanal gobernada por agentes...")

    unique_suffix = str(uuid.uuid4())[:8]

    # 1. Setup Data
    user = CustomUser.objects.create_user(
        username=f"artesano_sim_{unique_suffix}",
        email=f"art_sim_{unique_suffix}@test.com",
        password="password"
    )
    user.role = CustomUser.Role.ARTESANO
    user.save()

    provider = ProviderProfile.objects.create(
        usuario=user,
        nombre_comercial=f"Taller de Simulación {unique_suffix}",
        provider_type=ProviderProfile.ProviderTypes.ARTISAN,
        is_active=True
    )

    material = RawMaterial.objects.create(
        provider=provider,
        nombre="Lana",
        stock_actual=100.0,
        unidad_medida="kg"
    )

    order = WorkshopOrder.objects.create(
        provider=provider,
        producto_nombre="Poncho Tradicional",
        fecha_entrega_estimada="2024-12-31"
    )

    # 2. Execute via Agent Orchestrator
    print(f"Enviando directiva de producción para Orden {order.id}...")

    directive = {
        "domain": "operativa_turistica",
        "mission": {"type": "REGISTER_PRODUCTION"},
        "parameters": {
            "order_id": str(order.id),
            "material_id": str(material.id),
            "cantidad": 5,
            "descripcion": "Tejido de cuerpo principal"
        },
        "user_id": str(user.id)
    }

    result = sarita_orchestrator.handle_directive(directive)
    print(f"Resultado del agente: {result}")

    # 3. Verify results
    material.refresh_from_db()
    print(f"Nuevo stock de Lana: {material.stock_actual} kg (Esperado: 95.0)")

    if material.stock_actual == 95.0:
        print("¡SIMULACIÓN EXITOSA! Los agentes coordinaron la producción y el inventario.")
    else:
        print("ERROR: El stock no coincide.")

if __name__ == "__main__":
    simulate_artisan_production()
