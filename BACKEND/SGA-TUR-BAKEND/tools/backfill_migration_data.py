import os
import django
import uuid
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')
django.setup()

from api.models import Entity, Department, Municipality, CustomUser, GlobalRole, GlobalPermission
from apps.companies.models import Company
from apps.turismo.models.provider_models import TourismProvider, BusinessProfile
from apps.delivery.models import DeliveryCompany

def backfill():
    print("--- Starting Backfill ---")

    # 1. Base Locations
    dept, _ = Department.objects.get_or_create(name="Meta")
    mun, _ = Municipality.objects.get_or_create(name="Puerto Gaitán", department=dept)

    # 2. Entities
    ent_nac, _ = Entity.objects.get_or_create(
        slug="ente-nacional",
        defaults={"name": "ENTE NACIONAL DE TURISMO", "type": "nacional"}
    )
    ent_dept, _ = Entity.objects.get_or_create(
        slug="ente-departamental",
        defaults={"name": "ENTE DE TURISMO DEPARTAMENTAL", "type": "departamental"}
    )
    ent_mun, _ = Entity.objects.get_or_create(
        slug="ente-municipal",
        defaults={"name": "ENTE MUNICIPAL DE TURISMO", "type": "municipal"}
    )

    # 3. Superuser
    if not CustomUser.objects.filter(username="admin").exists():
        admin = CustomUser.objects.create_superuser("admin", "admin@sarita.com", "admin123")
        admin.role = CustomUser.Role.ADMIN
        admin.save()
        print("Superuser 'admin' created.")

    # 4. Global Roles (Authority Levels)
    soberano, _ = GlobalRole.objects.get_or_create(
        name="SOBERANO",
        defaults={"authority_level": 3, "is_system_role": True}
    )
    print("Global roles verified.")

    # 5. Companies (Required for Delivery)
    comp, _ = Company.objects.get_or_create(
        code="SLG",
        defaults={"name": "Sarita Logistics Corp"}
    )

    # 6. Delivery Company
    del_comp, _ = DeliveryCompany.objects.get_or_create(
        company=comp,
        defaults={"name": "Sarita Delivery Express"}
    )
    print("Delivery company verified.")

    print("--- Backfill Completed Successfully ---")

if __name__ == "__main__":
    backfill()
