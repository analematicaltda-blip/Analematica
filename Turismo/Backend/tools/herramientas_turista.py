# from langchain_core.tools import tool
from typing import List, Dict, Optional
from api.models import (
    CustomUser,
    Artesano,
    AtractivoTuristico,
    Publicacion,
    ElementoGuardado,
    Resena,
    Sugerencia
)
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

# --- SOLDADOS DE INTERACCIÓN Y PLANIFICACIÓN DE VIAJE ---

@tool
def guardar_elemento_viaje(turista_id: int, tipo_elemento: str, elemento_id: int) -> Dict:
    """
    (SOLDADO DE PLANIFICACIÓN) Guarda un elemento (artesano, atractivo) en la lista 'Mi Viaje' de un turista.
    `tipo_elemento` debe ser uno de: 'artesano', 'atractivo'.
    """
    print(f"--- 💥 SOLDADO (Planificación): ¡ACCIÓN! Guardando elemento {tipo_elemento} ID {elemento_id} para turista ID {turista_id}. ---")
    try:
        usuario = CustomUser.objects.get(id=turista_id, role=CustomUser.Role.TURISTA)

        if tipo_elemento == 'artesano':
            modelo = Artesano
        elif tipo_elemento == 'atractivo':
            modelo = AtractivoTuristico
        else:
            return {"status": "error", "message": "Tipo de elemento inválido. Use 'artesano' o 'atractivo'."}

        content_type = ContentType.objects.get_for_model(modelo)
        elemento, created = ElementoGuardado.objects.get_or_create(
            usuario=usuario,
            content_type=content_type,
            object_id=elemento_id
        )

        if not created:
            return {"status": "info", "message": "Este elemento ya estaba guardado en 'Mi Viaje'."}

        return {"status": "success", "message": f"Elemento '{elemento.content_object}' guardado en 'Mi Viaje'."}
    except ObjectDoesNotExist:
        return {"status": "error", "message": f"No se encontró el turista o el elemento especificado."}
    except Exception as e:
        return {"status": "error", "message": f"Ocurrió un error inesperado: {e}"}

@tool
def ver_elementos_guardados(turista_id: int) -> Dict:
    """
    (SOLDADO DE RECONOCIMIENTO) Consulta y devuelve la lista de todos los elementos que un turista ha guardado en 'Mi Viaje'.
    """
    print(f"--- 💥 SOLDADO (Reconocimiento): ¡ACCIÓN! Consultando 'Mi Viaje' para el turista ID {turista_id}. ---")
    try:
        usuario = CustomUser.objects.get(id=turista_id, role=CustomUser.Role.TURISTA)
        elementos = ElementoGuardado.objects.filter(usuario=usuario).select_related('content_type')

        if not elementos.exists():
            return {"status": "success", "message": "La lista 'Mi Viaje' está vacía."}

        lista_viaje = [
            {
                "id_guardado": el.id,
                "tipo": el.content_type.model,
                "nombre": str(el.content_object)
            }
            for el in elementos
        ]
        return {"status": "success", "mi_viaje": lista_viaje}
    except ObjectDoesNotExist:
        return {"status": "error", "message": f"No se encontró un turista con el ID {turista_id}."}

@tool
def eliminar_elemento_guardado(elemento_guardado_id: int) -> Dict:
    """
    (SOLDADO DE PLANIFICACIÓN) Elimina un elemento de la lista 'Mi Viaje' de un turista, usando el ID del elemento guardado.
    """
    print(f"--- 💥 SOLDADO (Planificación): ¡ACCIÓN! Eliminando elemento guardado ID {elemento_guardado_id}. ---")
    try:
        elemento = ElementoGuardado.objects.get(id=elemento_guardado_id)
        nombre_elemento = str(elemento.content_object)
        elemento.delete()
        return {"status": "success", "message": f"Elemento '{nombre_elemento}' eliminado de 'Mi Viaje'."}
    except ObjectDoesNotExist:
        return {"status": "error", "message": f"No se encontró un elemento guardado con el ID {elemento_guardado_id}."}

# --- SOLDADOS DE FEEDBACK Y PUNTUACIÓN ---

@tool
def dejar_resena(turista_id: int, tipo_elemento: str, elemento_id: int, calificacion: int, comentario: str) -> Dict:
    """
    (SOLDADO DE EVALUACIÓN) Permite a un turista dejar una reseña y calificación (de 1 a 5 estrellas)
    sobre un artesano. La reseña queda pendiente de aprobación.
    `tipo_elemento` debe ser 'artesano'.
    """
    print(f"--- 💥 SOLDADO (Evaluación): ¡ACCIÓN! Dejando reseña en {tipo_elemento} ID {elemento_id} por turista ID {turista_id}. ---")
    if not 1 <= calificacion <= 5:
        return {"status": "error", "message": "La calificación debe ser un número entre 1 y 5."}
    try:
        usuario = CustomUser.objects.get(id=turista_id, role=CustomUser.Role.TURISTA)

        if tipo_elemento == 'artesano':
            modelo = Artesano
        else:
            return {"status": "error", "message": "Solo se pueden dejar reseñas sobre 'artesano'."}

        content_object = modelo.objects.get(id=elemento_id)
        content_type = ContentType.objects.get_for_model(modelo)

        resena, created = Resena.objects.update_or_create(
            usuario=usuario,
            content_type=content_type,
            object_id=elemento_id,
            defaults={
                'calificacion': calificacion,
                'comentario': comentario,
                'aprobada': False # Las reseñas siempre deben ser moderadas
            }
        )

        accion = "creada" if created else "actualizada"
        return {"status": "success", "message": f"Tu reseña para '{content_object}' ha sido {accion} y está pendiente de aprobación. ¡Gracias por tu feedback!"}
    except ObjectDoesNotExist:
        return {"status": "error", "message": "No se encontró el turista o el elemento a reseñar."}

@tool
def enviar_sugerencia_queja_felicitacion(tipo_mensaje: str, mensaje: str, turista_id: Optional[int] = None, nombre_remitente: Optional[str] = None, email_remitente: Optional[str] = None) -> Dict:
    """
    (SOLDADO DE COMUNICACIONES) Envía una sugerencia, queja o felicitación a la administración.
    `tipo_mensaje` debe ser: 'SUGERENCIA', 'QUEJA', 'FELICITACION'.
    Si el `turista_id` es proporcionado, se asocia al usuario. Si no, se usan los campos de nombre y email.
    """
    print(f"--- 💥 SOLDADO (Comunicaciones): ¡ACCIÓN! Enviando un/a '{tipo_mensaje}'. ---")
    try:
        if tipo_mensaje not in Sugerencia.TipoMensaje.values:
            return {"status": "error", "message": f"Tipo de mensaje inválido. Válidos: {Sugerencia.TipoMensaje.labels}"}

        usuario = None
        if turista_id:
            usuario = CustomUser.objects.get(id=turista_id)

        Sugerencia.objects.create(
            usuario=usuario,
            nombre_remitente=nombre_remitente if not usuario else "",
            email_remitente=email_remitente if not usuario else "",
            tipo_mensaje=tipo_mensaje,
            mensaje=mensaje
        )
        return {"status": "success", "message": "Tu mensaje ha sido enviado correctamente. Gracias por ayudarnos a mejorar."}
    except ObjectDoesNotExist:
        return {"status": "error", "message": f"Si se provee un ID de turista, este debe existir."}

# --- SOLDADOS DE BÚSQUEDA Y CONSULTA ---

# @tool
# def buscar_informacion_general(termino_busqueda: str) -> Dict:
#     """
#     (SOLDADO DE INTELIGENCIA) Realiza una búsqueda general en prestadores, atractivos y publicaciones.
#     Devuelve una lista de resultados encontrados que coinciden con el término de búsqueda.
#     """
#     print(f"--- 💥 SOLDADO (Inteligencia): ¡ACCIÓN! Buscando información sobre '{termino_busqueda}'. ---")
#     try:
#         prestadores = PrestadorServicio.objects.filter(
#             Q(nombre_negocio__icontains=termino_busqueda) | Q(descripcion__icontains=termino_busqueda),
#             aprobado=True
#         )
#         atractivos = AtractivoTuristico.objects.filter(
#             Q(nombre__icontains=termino_busqueda) | Q(descripcion__icontains=termino_busqueda),
#             es_publicado=True
#         )
#         publicaciones = Publicacion.objects.filter(
#             Q(titulo__icontains=termino_busqueda) | Q(contenido__icontains=termino_busqueda),
#             estado=Publicacion.Status.PUBLICADO
#         )

#         resultados = {
#             "prestadores": [{"id": p.id, "nombre": p.nombre_negocio} for p in prestadores],
#             "atractivos": [{"id": a.id, "nombre": a.nombre} for a in atractivos],
#             "publicaciones": [{"id": p.id, "titulo": p.titulo} for p in publicaciones]
#         }

#         if not any(resultados.values()):
#             return {"status": "success", "message": f"No se encontró información para '{termino_busqueda}'."}

#         return {"status": "success", "data": resultados}
#     except Exception as e:
#         return {"status": "error", "message": f"Ocurrió un error inesperado durante la búsqueda: {e}"}


def get_turista_soldiers() -> List:
    """ Recluta y devuelve la Escuadra de Asistencia al Turista completa. """
    return [
        guardar_elemento_viaje,
        ver_elementos_guardados,
        eliminar_elemento_guardado,
        dejar_resena,
        enviar_sugerencia_queja_felicitacion,
        # buscar_informacion_general,
    ]