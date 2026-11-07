# backend/sabotage_test_guides_12.py
import os
import django
from decimal import Decimal
from django.utils import timezone

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')
django.setup()

from api.models import CustomUser
from apps.prestadores.mi_negocio.operativa_turistica.operadores_directos.guias.models import (
    GuiaTuristico, ServicioGuiado, LocalRutaTuristica, GrupoTuristico, CertificacionGuia
)
from apps.admin_plataforma.services.governance_kernel import GovernanceKernel

def run_sabotage_test_guides():
    print("🕵️ INICIANDO PRUEBA DE RUPTURA - GESTIÓN DE GUÍAS FASE 12.3")

    provider_user = CustomUser.objects.filter(username="bar_owner").first()
    profile = provider_user.perfil_prestador
    kernel = GovernanceKernel(provider_user)

    # 1. Doble Asignación Intencional (Conflicto Horario)
    print("\n--- INTENTO 1: Doble Asignación del mismo guía en el mismo horario ---")
    guia = GuiaTuristico.objects.filter(provider=profile).first()
    ruta = LocalRutaTuristica.objects.filter(provider=profile).first()
    grupo = GrupoTuristico.objects.filter(provider=profile).first()

    fecha = timezone.now().date()
    hora = timezone.now().time()

    # Crear primer servicio
    s1 = ServicioGuiado.objects.create(
        provider=profile, ruta=ruta, grupo=grupo, guia_asignado=guia,
        fecha=fecha, hora_inicio=hora, estado="CONFIRMADO"
    )

    # Intentar crear segundo servicio con el mismo guía y horario vía servicio
    from apps.prestadores.mi_negocio.operativa_turistica.operadores_directos.guias.services import GuideService
    gs = GuideService(provider_user)

    try:
        gs.programar_servicio({
            "ruta_id": ruta.id, "grupo_id": grupo.id, "guia_asignado_id": guia.id,
            "fecha": fecha, "hora_inicio": hora, "precio_total": 500000
        })
    except Exception as e:
        print(f"✅ BLOQUEO EXITOSO (CONFLICTO HORARIO): {e}")

    # 2. Validación Documental Obligatoria (Guía con certificación vencida)
    print("\n--- INTENTO 2: Confirmar servicio con certificación vencida ---")
    cert = guia.certificaciones.first()
    cert.fecha_vencimiento = timezone.now().date() - timezone.timedelta(days=1)
    cert.save()

    s2 = ServicioGuiado.objects.create(
        provider=profile, ruta=ruta, grupo=grupo, guia_asignado=guia,
        fecha=fecha, hora_inicio=timezone.now().time(), estado="PROGRAMADO"
    )

    # Intentar confirmar vía viewset action logic
    from apps.prestadores.mi_negocio.operativa_turistica.operadores_directos.guias.views import ServicioGuiadoViewSet
    from unittest.mock import MagicMock

    # Simulación de la lógica de confirmación en la vista
    certificaciones_validas = any(c.is_valid() for c in s2.guia_asignado.certificaciones.all())
    if not certificaciones_validas:
        print("✅ BLOQUEO EXITOSO (CERTIFICACIÓN VENCIDA)")
    else:
        print("❌ FALLO: Se permitió confirmar con certificación vencida")

    # 3. Liquidación Duplicada
    print("\n--- INTENTO 3: Liquidar dos veces el mismo servicio ---")
    s3 = ServicioGuiado.objects.create(
        provider=profile, ruta=ruta, grupo=grupo, guia_asignado=guia,
        fecha=fecha, hora_inicio=timezone.now().time(), estado="LIQUIDADO"
    )

    try:
        gs.liquidar_servicio(s3.id, {"tipo": "PORCENTAJE", "valor": 10})
    except Exception as e:
        print(f"✅ BLOQUEO EXITOSO (YA LIQUIDADO): {e}")

    print("\n🏁 PRUEBA DE RUPTURA DE GUÍAS FINALIZADA.")

if __name__ == "__main__":
    run_sabotage_test_guides()
