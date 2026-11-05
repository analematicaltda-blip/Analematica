# backend/simulate_guide_services_12.py
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
from apps.prestadores.mi_negocio.operativa_turistica.operadores_directos.guias.models import (
    GuiaTuristico, CertificacionGuia, LocalRutaTuristica, GrupoTuristico, ServicioGuiado
)
from apps.admin_plataforma.services.governance_kernel import GovernanceKernel
from apps.companies.models import Company

def simulate_guide_services():
    print("🚀 INICIANDO SIMULACIÓN DE SERVICIOS GUIADOS FASE 12.2")

    # 1. Setup
    company = Company.objects.first()
    provider_user = CustomUser.objects.filter(username="bar_owner").first() # Reutilizando
    profile = ProviderProfile.objects.filter(usuario=provider_user).first()

    # 2. Crear Guías y Certificaciones
    print("--- Creando guías y certificaciones... ---")
    guides = []
    for i in range(1, 6):
        u, _ = CustomUser.objects.get_or_create(
            username=f"guide_{i}",
            defaults={"email": f"guide{i}@test.com", "role": "FUNCIONARIO_PROFESIONAL"}
        )
        g, _ = GuiaTuristico.objects.get_or_create(
            provider=profile,
            usuario=u,
            defaults={"identificacion": f"ID-GUIDE-{i}", "nivel": "SENIOR"}
        )
        CertificacionGuia.objects.get_or_create(
            provider=profile,
            guia=g,
            tipo_certificacion="Guía Profesional",
            defaults={
                "entidad_emisora": "Ministerio de Turismo",
                "issue_date": timezone.now().date() - timezone.timedelta(days=100),
                "fecha_vencimiento": timezone.now().date() + timezone.timedelta(days=365),
                "estado_validacion": "VALIDADO"
            }
        )
        guides.append(g)

    # 3. Crear Rutas
    ruta_caño, _ = LocalRutaTuristica.objects.get_or_create(
        provider=profile,
        nombre="Aventura en Caño Cristales",
        defaults={"descripcion": "Tour de día completo", "duracion_estimada_horas": 8}
    )

    # 4. Crear Grupos
    grupo, _ = GrupoTuristico.objects.get_or_create(
        provider=profile,
        nombre="Exploradores Bogotá",
        defaults={"numero_turistas": 12, "contacto_principal": "Juan Perez"}
    )

    # 5. Programar Servicios Concurrentes
    print("--- Programando servicios... ---")
    kernel = GovernanceKernel(provider_user)

    servicios = []
    for i in range(1, 11):
        # Programamos 10 servicios en diferentes horarios
        hora = (timezone.now() + timezone.timedelta(hours=i)).time()
        s = ServicioGuiado.objects.create(
            provider=profile,
            ruta=ruta_caño,
            fecha=timezone.now().date(),
            hora_inicio=hora,
            grupo=grupo,
            guia_asignado=random.choice(guides),
            precio_total=Decimal('500000'),
            estado=ServicioGuiado.Estado.PROGRAMADO
        )
        servicios.append(s)

    # 6. Confirmar y Liquidar
    print("--- Confirmando y Liquidando servicios... ---")
    for s in servicios:
        # Confirmación (Verifica certificaciones)
        try:
            s.estado = ServicioGuiado.Estado.CONFIRMADO
            s.save()

            # Liquidación vía Gobernanza
            kernel.resolve_and_execute("LIQUIDATE_GUIDE_COMMISSION", {
                "servicio_id": str(s.id),
                "tipo": "PORCENTAJE",
                "valor": 15, # 15% comisión
                "user_id": provider_user.id
            })
        except Exception as e:
            print(f"Error en servicio {s.id}: {e}")

    print(f"\n📊 RESULTADOS SIMULACIÓN GUÍAS:")
    print(f"✅ Guías en red: {len(guides)}")
    print(f"✅ Servicios procesados: {len(servicios)}")
    print(f"✅ Comisiones liquidadas: {ServicioGuiado.objects.filter(estado='LIQUIDADO').count()}")

    if ServicioGuiado.objects.filter(estado='LIQUIDADO').exists():
        print("\n🏆 VALIDACIÓN FASE 12.2 EXITOSA: Flujo de guías operativo.")

if __name__ == "__main__":
    simulate_guide_services()
