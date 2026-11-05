# from langchain_core.tools import tool
from typing import List, Dict, Optional
from api.models import (
    CustomUser,
    PaginaInstitucional,
    ContenidoMunicipio,
    HechoHistorico,
    PlantillaVerificacion,
    ItemVerificacion,
    Verificacion,
    RespuestaItemVerificacion,
    AsistenciaCapacitacion,
    Publicacion
)
from django.core.exceptions import ObjectDoesNotExist

# --- SOLDADOS DE GESTIÓN DE CONTENIDO INSTITUCIONAL ---

@tool
def gestionar_pagina_institucional(slug: str, **kwargs) -> Dict:
    """
    (SOLDADO DE CONTENIDO) Crea o actualiza una página institucional (ej. 'secretaria-turismo').
    `slug` es el identificador de la página. Los demás argumentos son los campos a actualizar
    (ej. `titulo_banner`, `contenido_principal`).
    """
    print(f"--- 💥 SOLDADO (Funcionario): ¡ACCIÓN! Gestionando página institucional '{slug}'. ---")
    try:
        pagina, created = PaginaInstitucional.objects.get_or_create(slug=slug)
        for key, value in kwargs.items():
            if hasattr(pagina, key):
                setattr(pagina, key, value)
        pagina.save()
        accion = "creada" if created else "actualizada"
        return {"status": "success", "message": f"Página institucional '{slug}' {accion} correctamente."}
    except Exception as e:
        return {"status": "error", "message": f"Error al gestionar la página: {e}"}

@tool
def gestionar_contenido_municipio(seccion: str, titulo: str, contenido: str, **kwargs) -> Dict:
    """
    (SOLDADO DE CONTENIDO) Crea o actualiza un bloque de contenido en la página del municipio.
    `seccion` debe ser un valor válido como 'INTRODUCCION', 'COMO_LLEGAR'. `titulo` es el identificador único dentro de la sección.
    """
    print(f"--- 💥 SOLDADO (Funcionario): ¡ACCIÓN! Gestionando contenido '{titulo}' en sección '{seccion}'. ---")
    if seccion not in ContenidoMunicipio.Seccion.values:
        return {"status": "error", "message": f"Sección inválida. Válidas: {ContenidoMunicipio.Seccion.labels}"}
    try:
        bloque, created = ContenidoMunicipio.objects.update_or_create(
            seccion=seccion,
            titulo=titulo,
            defaults={'contenido': contenido, **kwargs}
        )
        accion = "creado" if created else "actualizado"
        return {"status": "success", "message": f"Bloque de contenido '{titulo}' {accion}."}
    except Exception as e:
        return {"status": "error", "message": f"Error al gestionar contenido del municipio: {e}"}

# --- SOLDADOS DE GESTIÓN DE VERIFICACIONES ---

@tool
def crear_plantilla_verificacion(nombre: str, descripcion: str, categoria_prestador_id: Optional[int] = None) -> Dict:
    """
    (SOLDADO DE DOCTRINA) Crea una nueva plantilla de verificación (checklist).
    Se puede asociar opcionalmente a una categoría de prestador por su ID.
    """
    print(f"--- 💥 SOLDADO (Funcionario): ¡ACCIÓN! Creando plantilla de verificación '{nombre}'. ---")
    try:
        plantilla = PlantillaVerificacion.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            categoria_prestador_id=categoria_prestador_id
        )
        return {"status": "success", "plantilla_id": plantilla.id, "message": "Plantilla de verificación creada."}
    except Exception as e:
        return {"status": "error", "message": f"Error al crear la plantilla: {e}"}

@tool
def agregar_item_a_plantilla(plantilla_id: int, texto_requisito: str, puntaje: int, es_obligatorio: bool = True) -> Dict:
    """
    (SOLDADO DE DOCTRINA) Agrega un nuevo ítem o requisito a una plantilla de verificación existente.
    """
    print(f"--- 💥 SOLDADO (Funcionario): ¡ACCIÓN! Agregando ítem a plantilla ID {plantilla_id}. ---")
    try:
        item = ItemVerificacion.objects.create(
            plantilla_id=plantilla_id,
            texto_requisito=texto_requisito,
            puntaje=puntaje,
            es_obligatorio=es_obligatorio
        )
        return {"status": "success", "item_id": item.id, "message": "Ítem agregado a la plantilla."}
    except Exception as e:
        return {"status": "error", "message": f"Error al agregar el ítem: {e}"}

@tool
def registrar_respuesta_item_verificacion(verificacion_id: int, item_id: int, cumple: bool, justificacion: str = "") -> Dict:
    """
    (SOLDADO DE CAMPO) Registra la respuesta (si cumple o no) para un ítem específico de una verificación en curso.
    """
    print(f"--- 💥 SOLDADO (Funcionario): ¡ACCIÓN! Registrando respuesta para ítem ID {item_id} en verificación ID {verificacion_id}. ---")
    try:
        respuesta, created = RespuestaItemVerificacion.objects.update_or_create(
            verificacion_id=verificacion_id,
            item_original_id=item_id,
            defaults={'cumple': cumple, 'justificacion': justificacion}
        )
        # La señal post_save en Verificacion se encargará de recalcular el puntaje total.
        accion = "registrada" if created else "actualizada"
        return {"status": "success", "message": f"Respuesta {accion}."}
    except Exception as e:
        return {"status": "error", "message": f"Error al registrar la respuesta: {e}"}

# --- SOLDADOS DE GESTIÓN DE CAPACITACIONES ---

@tool
def registrar_asistencia_capacitacion(capacitacion_id: int, lista_emails_asistentes: List[str]) -> Dict:
    """
    (SOLDADO DE FORMACIÓN) Registra la asistencia de múltiples usuarios a una capacitación.
    `capacitacion_id` es el ID de la publicación de tipo 'CAPACITACION'.
    `lista_emails_asistentes` es una lista de los correos electrónicos de los prestadores/artesanos que asistieron.
    """
    print(f"--- 💥 SOLDADO (Funcionario): ¡ACCIÓN! Registrando asistencia para capacitación ID {capacitacion_id}. ---")
    try:
        capacitacion = Publicacion.objects.get(id=capacitacion_id, tipo=Publicacion.Tipo.CAPACITACION)
        usuarios = CustomUser.objects.filter(email__in=lista_emails_asistentes)

        asistencias_creadas = 0
        for usuario in usuarios:
            asistencia, created = AsistenciaCapacitacion.objects.get_or_create(
                capacitacion=capacitacion,
                usuario=usuario
            )
            if created:
                asistencias_creadas += 1

        # La señal post_save en AsistenciaCapacitacion recalculará los puntajes.
        return {"status": "success", "message": f"Se registraron {asistencias_creadas} nuevas asistencias de {len(lista_emails_asistentes)} usuarios."}
    except ObjectDoesNotExist:
        return {"status": "error", "message": f"No se encontró una capacitación con el ID {capacitacion_id}."}
    except Exception as e:
        return {"status": "error", "message": f"Error al registrar asistencia: {e}"}


def get_funcionario_soldiers() -> List:
    """ Recluta y devuelve la Escuadra de Funcionarios completa. """
    return [
        gestionar_pagina_institucional,
        gestionar_contenido_municipio,
        crear_plantilla_verificacion,
        agregar_item_a_plantilla,
        registrar_respuesta_item_verificacion,
        registrar_asistencia_capacitacion,
    ]