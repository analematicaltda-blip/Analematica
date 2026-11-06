import os
import django
import math
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')
django.setup()

from api.models import CustomUser, AtractivoTuristico, Entity, Publicacion
from apps.turismo.models.provider_models import TourismProvider
from rest_framework.test import APIClient

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat / 2) * math.sin(dLat / 2) +         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *         math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def test_directory_flows():
    print("\n--- Testing Territorial Tourism Directory ---")
    admin = CustomUser.objects.get(username="admin")
    ent = Entity.objects.get(slug="ente-municipal")

    # Prueba 1: Registro de Empresa
    provider = TourismProvider.objects.create(
        name="Llanos Express Hotel",
        provider_type="HOTEL",
        owner=admin,
        location={"lat": 4.312, "lng": -72.082, "address": "Calle Principal #5"},
        contact={"phone": "+573101234567", "whatsapp": "573101234567", "email": "info@llanos.com"},
        status="ACTIVE"
    )
    print(f"Prueba 1: Empresa registrada -> {provider.name}")

    # Prueba 2: Visualización en Mapa
    print(f"Prueba 2: Ubicación en Mapa -> lat: {provider.location['lat']}, lng: {provider.location['lng']}")

    # Prueba 3: WhatsApp Link
    wa_link = f"https://wa.me/{provider.contact['whatsapp']}"
    print(f"Prueba 3: WhatsApp Link -> {wa_link}")

    # Prueba 4: Cómo llegar (Google Maps)
    maps_link = f"https://www.google.com/maps/search/?api=1&query={provider.location['lat']},{provider.location['lng']}"
    print(f"Prueba 4: Google Maps Link -> {maps_link}")

    # Prueba 5: Relación con Atractivo
    atractivo = AtractivoTuristico.objects.create(
        nombre="Río Manacacías", slug="rio-manacacias",
        latitud=4.315, longitud=-72.085,
        entity=ent, categoria_color="BLANCO",
        descripcion="Espectacular río", como_llegar="Cerca al pueblo"
    )
    dist = calculate_distance(atractivo.latitud, atractivo.longitud, provider.location['lat'], provider.location['lng'])
    print(f"Prueba 5: Atractivo '{atractivo.nombre}' cercano a '{provider.name}' (Distancia: {dist:.2f} km)")

    if dist < 2.0:
        print("SUCCESS: Sistema puede sugerir servicios cercanos.")
    else:
        print("FAIL: Distancia fuera de rango esperado.")

if __name__ == "__main__":
    try:
        test_directory_flows()
    except Exception as e:
        import traceback
        traceback.print_exc()
