import os
import django
import sys

# Configurar el entorno de Django
sys.path.append('/workspace/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')
django.setup()

from apps.sadi_agent.models import SemanticDomain, Intent

def seed_coverage_intents():
    print("Seeding Coverage Intents for 5 Domains...")

    # Dominios
    domains = {
        "comercial": "Gestión de ventas y planes",
        "contable": "Registro y reportes contables",
        "financiero": "Tesorería y movimientos de dinero",
        "operativo": "Gestión de recursos y logística",
        "archivistico": "Gestión documental y archivo"
    }

    for name, desc in domains.items():
        dom, _ = SemanticDomain.objects.get_or_create(name=name, defaults={"description": desc})

        # Acciones comunes por dominio
        if name == "comercial":
            Intent.objects.get_or_create(domain=dom, name="ERP_VIEW_SALES_STATS", description="Consultar estadísticas de ventas.")
        elif name == "contable":
            Intent.objects.get_or_create(domain=dom, name="ERP_CREATE_VOUCHER", description="Crear un comprobante contable.")
        elif name == "financiero":
            Intent.objects.get_or_create(domain=dom, name="ERP_VIEW_CASH_FLOW", description="Consultar el flujo de caja actual.")
        elif name == "operativo":
            Intent.objects.get_or_create(domain=dom, name="ERP_MANAGE_RESOURCES", description="Gestionar recursos de la plataforma.")
        elif name == "archivistico":
            Intent.objects.get_or_create(domain=dom, name="ERP_SEARCH_DOCUMENT", description="Buscar un documento en el archivo.")

    print("Coverage Seed completed.")

if __name__ == "__main__":
    seed_coverage_intents()
