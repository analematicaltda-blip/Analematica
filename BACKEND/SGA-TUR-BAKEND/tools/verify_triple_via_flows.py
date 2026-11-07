import os
import django
import uuid
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')
django.setup()

from api.models import CustomUser, GovernmentProfile, Entity
from apps.turismo.models.provider_models import TourismProvider, TourismService
from apps.delivery.models import DeliveryService, Driver, DeliveryCompany, Vehicle
from rest_framework.test import APIClient
from django.urls import reverse

def test_flow_1_government():
    print("\n--- Testing Flow 1: Government Hierarchy ---")
    client = APIClient()
    admin = CustomUser.objects.get(username="admin")
    client.force_authenticate(user=admin)

    ent_nac = Entity.objects.get(slug="ente-nacional")
    ent_dept = Entity.objects.get(slug="ente-departamental")
    ent_mun = Entity.objects.get(slug="ente-municipal")

    url = reverse('user-admin-list')

    # 1. Admin creates National Director
    res = client.post(url, {
        "username": "nac_dir", "email": "nac@gov.co", "password": "pass", "role": "DIRECTIVO_NACIONAL",
        "government_profile": {"entity": str(ent_nac.id), "cargo": "Director Nacional", "nivel": "NACIONAL"}
    }, format='json')
    print(f"Admin creates National Director: {res.status_code}")
    if res.status_code != 201:
        print(f"Error: {res.data}")
    nac_dir = CustomUser.objects.get(username="nac_dir")

    # 2. National Director creates Dept Director
    client.force_authenticate(user=nac_dir)
    res = client.post(url, {
        "username": "dept_dir", "email": "dept@gov.co", "password": "pass", "role": "DIRECTIVO_DEPARTAMENTAL",
        "government_profile": {"entity": ent_dept.id, "cargo": "Director Dept", "nivel": "DEPARTAMENTAL"}
    }, format='json')
    print(f"National Director creates Dept Director: {res.status_code}")
    dept_dir = CustomUser.objects.get(username="dept_dir")

    # 3. Dept Director creates Mun Director
    client.force_authenticate(user=dept_dir)
    res = client.post(url, {
        "username": "mun_dir", "email": "mun@gov.co", "password": "pass", "role": "DIRECTIVO_MUNICIPAL",
        "government_profile": {"entity": ent_mun.id, "cargo": "Director Mun", "nivel": "MUNICIPAL"}
    }, format='json')
    print(f"Dept Director creates Mun Director: {res.status_code}")
    mun_dir = CustomUser.objects.get(username="mun_dir")

    # 4. Mun Director creates Professional Official
    client.force_authenticate(user=mun_dir)
    res = client.post(url, {
        "username": "mun_prof", "email": "prof@gov.co", "password": "pass", "role": "FUNCIONARIO_PROFESIONAL",
        "government_profile": {"entity": ent_mun.id, "cargo": "Profesional Mun", "nivel": "MUNICIPAL"}
    }, format='json')
    print(f"Mun Director creates Professional Official: {res.status_code}")

def test_flow_2_business():
    print("\n--- Testing Flow 2: Business ---")
    client = APIClient()
    admin = CustomUser.objects.get(username="admin")
    client.force_authenticate(user=admin)

    # 1. Register Owner
    url_user = reverse('user-admin-list')
    res = client.post(url_user, {
        "username": "hotel_owner", "email": "hotel@owner.com", "password": "pass", "role": "BUSINESS_OWNER"
    }, format='json')
    print(f"Register Owner: {res.status_code}")
    owner = CustomUser.objects.get(username="hotel_owner")

    # 2. Create Provider
    client.force_authenticate(user=owner)
    provider = TourismProvider.objects.create(
        name="Hotel Paraíso", provider_type="HOTEL", owner=owner,
        location={"address": "Calle 1"}, contact={"phone": "123"}
    )
    print(f"Provider created: {provider.name}")

    # 3. Create Service
    url_service = "/api/v1/turismo/v1/tourism-services/"
    res = client.post(url_service, {
        "provider": provider.id, "service_type": "ACCOMMODATION",
        "name": "Suite Real", "description": "Lujo", "price": "150000.00", "capacity": 2
    }, format='json')
    print(f"Create Service: {res.status_code}")

def test_flow_3_tourist():
    print("\n--- Testing Flow 3: Tourist ---")
    client = APIClient()
    admin = CustomUser.objects.get(username="admin")
    client.force_authenticate(user=admin)

    # 1. Register Tourist
    url_user = reverse('user-admin-list')
    res = client.post(url_user, {
        "username": "turista_pepe", "email": "pepe@gmail.com", "password": "pass", "role": "TURISTA",
        "tourist_profile": {"passport_number": "PP123", "nationality": "Española"}
    }, format='json')
    print(f"Register Tourist: {res.status_code}")
    pepe = CustomUser.objects.get(username="turista_pepe")

    # 2. Search Services
    client.force_authenticate(user=pepe)
    url_search = "/api/v1/turismo/v1/tourism-services/"
    res = client.get(url_search)
    print(f"Search Services (Count): {len(res.data.get('results', []))}")

    # 3. Create Reservation
    if len(res.data.get('results', [])) > 0:
        service_id = res.data['results'][0]['id']
        provider_id = res.data['results'][0]['provider']
        url_res = "/api/v1/turismo/v1/tourism-reservations/"
        res = client.post(url_res, {
            "provider": provider_id, "service": service_id, "customer": pepe.id,
            "start_date": "2026-05-01T10:00:00Z", "end_date": "2026-05-05T10:00:00Z",
            "total_price": "600000.00"
        }, format='json')
        print(f"Create Reservation: {res.status_code}")

def test_flow_4_delivery():
    print("\n--- Testing Flow 4: Delivery ---")
    client = APIClient()
    admin = CustomUser.objects.get(username="admin")
    client.force_authenticate(user=admin)

    # 1. Register Driver
    url_user = reverse('user-admin-list')
    res = client.post(url_user, {
        "username": "driver_juan", "email": "juan@delivery.com", "password": "pass", "role": "DELIVERY_DRIVER",
        "delivery_profile": {"company_name": "Sarita Delivery Express", "vehicle_type": "MOTO"}
    }, format='json')
    print(f"Register Driver: {res.status_code}")
    juan = CustomUser.objects.get(username="driver_juan")

    # Setup Driver Profile in Delivery DB
    del_comp = DeliveryCompany.objects.using('delivery_db').first()
    driver, _ = Driver.objects.using('delivery_db').get_or_create(
        user_id=juan.id,
        defaults={"delivery_company": del_comp, "license_number": "LIC-123"}
    )
    vehicle, _ = Vehicle.objects.using('delivery_db').get_or_create(
        plate="XYZ-123",
        defaults={"vehicle_type": "MOTO", "delivery_company": del_comp}
    )

    # 2. Create and Assign Order
    client.force_authenticate(user=admin)
    url_del = "/api/v1/operations/delivery/services/"
    res = client.post(url_del, {
        "tourist_id": juan.id, # Using juan as a dummy tourist for test
        "origin_address": "Calle A", "destination_address": "Calle B",
        "delivery_company": str(del_comp.id), "driver": str(driver.id), "vehicle": str(vehicle.id),
        "status": "EN_RUTA",
        "estimated_price": "10000.00"
    }, format='json')
    print(f"Create/Assign Delivery: {res.status_code}")
    if res.status_code != 201:
        print(f"Error: {res.data}")
        return
    delivery_id = res.data['id']

    # 3. Complete Delivery
    client.force_authenticate(user=juan)
    res = client.patch(f"{url_del}{delivery_id}/", {
        "status": "ENTREGADO",
        "firma": "JUAN_SIGNATURE",
        "latitud": 1.23,
        "longitud": -73.45
    }, format='json')
    print(f"Complete Delivery: {res.status_code}")

if __name__ == "__main__":
    # Clean up previous tests manually to avoid Cross-DB deletion issues
    usernames = ["nac_dir", "dept_dir", "mun_dir", "mun_prof", "hotel_owner", "turista_pepe", "driver_juan"]
    for uname in usernames:
        u = CustomUser.objects.filter(username=uname).first()
        if u:
            # Cleanup delivery profile specifically if it exists due to UNIQUE constraints
            Driver.objects.using('delivery_db').filter(user_id=u.id).delete()
            try:
                u.delete()
            except Exception as e:
                pass

    test_flow_1_government()
    test_flow_2_business()
    test_flow_3_tourist()
    test_flow_4_delivery()
