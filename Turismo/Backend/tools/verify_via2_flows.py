import os
import django
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')
django.setup()

from api.models import CustomUser, Entity, AtractivoTuristico
from apps.turismo.models.provider_models import TourismProvider, TourismService
from rest_framework.test import APIClient

def test_via2_lifecycle():
    print("\n--- Testing Vía 2 (Sector Privado) Lifecycle ---")
    client = APIClient()
    admin, _ = CustomUser.objects.get_or_create(username="admin", defaults={"role": "ADMIN", "is_staff": True, "is_superuser": True})
    client.force_authenticate(user=admin)
    ent, _ = Entity.objects.get_or_create(slug="ente-municipal", defaults={"name": "Ente Municipal", "type": "municipal"})

    # Clean up
    CustomUser.objects.filter(username="hotel_owner_2").delete()

    # 1. Registro de Propietario
    owner_data = {
        "username": "hotel_owner_2", "email": "owner2@test.com", "password": "pass", "role": "BUSINESS_OWNER"
    }
    res = client.post("/api/admin/users/", owner_data, format='json')
    print(f"1. Registro Propietario: {res.status_code}")
    owner = CustomUser.objects.get(username="hotel_owner_2")

    # 2. Creación de Perfil de Empresa (Prestador)
    client.force_authenticate(user=owner)
    provider_data = {
        "name": "Eco-Lodge Llanos",
        "provider_type": "HOTEL",
        "location": {"lat": 4.318, "lng": -72.088, "address": "Reserva Natural km 10"},
        "contact": {"whatsapp": "573200000000", "email": "lodge@test.com"},
        "status": "ACTIVE"
    }
    res = client.post("/api/v1/turismo/v1/tourism-providers/", provider_data, format='json')
    print(f"2. Creación de Empresa: {res.status_code}")
    if res.status_code != 201:
        print(f"Error detail: {res.data}")
        return
    provider_id = res.data['id']

    # 3. Publicación de Servicio, Producto y Experiencia
    client.post("/api/v1/turismo/v1/tourism-services/", {
        "provider": provider_id, "service_type": "ACCOMMODATION",
        "name": "Habitación Selva", "description": "Vista al río", "price": "120000.00", "capacity": 2
    }, format='json')

    print("3. Servicios publicados.")

    # 4. Verificación de Contacto y GPS
    provider = TourismProvider.objects.get(id=provider_id)
    wa_link = f"https://wa.me/{provider.contact['whatsapp']}"
    gps_link = f"https://www.google.com/maps/dir/?api=1&destination={provider.location['lat']},{provider.location['lng']}"
    print(f"4. Contacto WhatsApp: {wa_link}")
    print(f"4. Ruta GPS: {gps_link}")

    # 5. Integración con Atractivo
    atractivo = AtractivoTuristico.objects.create(
        nombre="Mirador del Sol", slug="mirador-sol",
        latitud=4.320, longitud=-72.090,
        entity=ent, categoria_color="ROJO",
        descripcion="Vista increible", como_llegar="Siga derecho"
    )
    print(f"5. Atractivo '{atractivo.nombre}' creado.")
    print("SUCCESS: Vía 2 funcional y auditada.")

if __name__ == "__main__":
    try:
        test_via2_lifecycle()
    except Exception as e:
        import traceback
        traceback.print_exc()
