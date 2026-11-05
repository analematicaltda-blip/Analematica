# from langchain_core.tools import tool
from typing import List, Dict, Optional
from api.models import (
    CustomUser,
    SiteConfiguration,
    MenuItem,
    HomePageComponent,
    Resena,
    Sugerencia,
    AuditLog,
    ScoringRule
)
from django.core.exceptions import ObjectDoesNotExist

# --- SOLDADOS DE GESTIÓN DE USUARIOS ---

@tool
def crear_usuario(email: str, nombre_usuario: str, rol: str) -> Dict:
    """
    (SOLDADO DE RECLUTAMIENTO) Crea un nuevo usuario en el sistema con un rol específico.
    `rol` debe ser uno de los valores válidos en CustomUser.Role (ej. 'FUNCIONARIO_DIRECTIVO').
    La contraseña inicial es temporal y se recomienda al usuario cambiarla.
    """
    print(f"--- 💥 SOLDADO (Admin): ¡ACCIÓN! Creando usuario {email} con rol {rol}. ---")
    if rol not in CustomUser.Role.values:
        return {"status": "error", "message": f"Rol '{rol}' inválido. Válidos: {CustomUser.Role.labels}"}
    try:
        if CustomUser.objects.filter(email=email).exists():
            return {"status": "error", "message": "El email ya está en uso."}

        user = CustomUser.objects.create_user(
            username=nombre_usuario,
            email=email,
            role=rol
        )
        user.set_password("temporal12345")
        user.save()
        return {"status": "success", "user_id": user.id, "message": "Usuario creado con contraseña temporal."}
    except Exception as e:
        return {"status": "error", "message": f"Error al crear usuario: {e}"}

@tool
def actualizar_rol_usuario(user_id: int, nuevo_rol: str) -> Dict:
    """
    (SOLDADO DE PROMOCIÓN) Actualiza el rol de un usuario existente.
    `nuevo_rol` debe ser uno de los valores válidos en CustomUser.Role.
    """
    print(f"--- 💥 SOLDADO (Admin): ¡ACCIÓN! Cambiando rol del usuario {user_id} a {nuevo_rol}. ---")
    if nuevo_rol not in CustomUser.Role.values:
        return {"status": "error", "message": f"Rol '{nuevo_rol}' inválido. Válidos: {CustomUser.Role.labels}"}
    try:
        user = CustomUser.objects.get(id=user_id)
        user.role = nuevo_rol
        user.save(update_fields=['role'])
        return {"status": "success", "message": f"Rol del usuario '{user.username}' actualizado a {user.get_role_display()}."}
    except ObjectDoesNotExist:
        return {"status": "error", "message": f"Usuario con ID {user_id} no encontrado."}

# --- SOLDADOS DE CONFIGURACIÓN DEL SITIO ---

@tool
def actualizar_configuracion_sitio(**kwargs) -> Dict:
    """
    (SOLDADO DE INGENIERÍA) Actualiza la configuración general del sitio.
    Acepta como argumentos los nombres de los campos del modelo SiteConfiguration,
    como `nombre_entidad_principal`, `correo_institucional`, `social_facebook`, etc.
    """
    print(f"--- 💥 SOLDADO (Admin): ¡ACCIÓN! Actualizando la configuración del sitio. ---")
    try:
        config = SiteConfiguration.load()
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        config.save()
        return {"status": "success", "message": "Configuración del sitio actualizada."}
    except Exception as e:
        return {"status": "error", "message": f"Error al actualizar la configuración: {e}"}

@tool
def actualizar_reglas_puntuacion(**kwargs) -> Dict:
    """
    (SOLDADO DE ESTRATEGIA) Actualiza las reglas de puntuación del sistema.
    Acepta: `puntos_asistencia_capacitacion`, `puntos_por_estrella_reseña`, `puntos_completar_formulario`.
    """
    print(f"--- 💥 SOLDADO (Admin): ¡ACCIÓN! Actualizando reglas de puntuación. ---")
    try:
        rules = ScoringRule.load()
        for key, value in kwargs.items():
            if hasattr(rules, key):
                setattr(rules, key, value)
        rules.save()
        return {"status": "success", "message": "Reglas de puntuación actualizadas."}
    except Exception as e:
        return {"status": "error", "message": f"Error al actualizar las reglas: {e}"}

# --- SOLDADOS DE MODERACIÓN Y SUPERVISIÓN ---

@tool
def aprobar_resena(resena_id: int, aprobar: bool) -> Dict:
    """
    (SOLDADO DE MODERACIÓN) Aprueba o desaprueba una reseña dejada por un turista.
    Solo las reseñas aprobadas son visibles y cuentan para la puntuación.
    """
    print(f"--- 💥 SOLDADO (Admin): ¡ACCIÓN! {'Aprobando' if aprobar else 'Rechazando'} reseña ID {resena_id}. ---")
    try:
        resena = Resena.objects.get(id=resena_id)
        resena.aprobada = aprobar
        resena.save(update_fields=['aprobada'])
        # La señal post_save en el modelo Resena se encargará de recalcular la puntuación.
        estado = "aprobada" if aprobar else "rechazada"
        return {"status": "success", "message": f"La reseña ha sido {estado}."}
    except ObjectDoesNotExist:
        return {"status": "error", "message": f"Reseña con ID {resena_id} no encontrada."}

@tool
def ver_registros_auditoria(limite: int = 20) -> Dict:
    """
    (SOLDADO DE VIGILANCIA) Consulta y devuelve los últimos N registros de la bitácora de auditoría.
    """
    print(f"--- 💥 SOLDADO (Admin): ¡ACCIÓN! Consultando los últimos {limite} registros de auditoría. ---")
    try:
        logs = AuditLog.objects.select_related('user').order_by('-timestamp')[:limite]
        registros = [
            {
                "fecha": log.timestamp.isoformat(),
                "usuario": log.user.username if log.user else "Sistema",
                "accion": log.get_action_display(),
                "detalles": log.details
            }
            for log in logs
        ]
        return {"status": "success", "registros": registros}
    except Exception as e:
        return {"status": "error", "message": f"Error al consultar auditoría: {e}"}


def get_admin_soldiers() -> List:
    """ Recluta y devuelve la Escuadra de Administración completa. """
    return [
        crear_usuario,
        actualizar_rol_usuario,
        actualizar_configuracion_sitio,
        actualizar_reglas_puntuacion,
        aprobar_resena,
        ver_registros_auditoria,
    ]