# from langchain_core.tools import tool
from typing import List, Dict, Optional
from api.models import Publicacion, CustomUser
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.text import slugify
from datetime import datetime

# --- SOLDADOS DE GESTIÓN DE CONTENIDOS (CRUD) ---

@tool
def crear_publicacion(
    autor_id: int,
    tipo: str,
    titulo: str,
    contenido: str,
    imagen_principal_path: Optional[str] = None,
    subcategoria_evento: Optional[str] = None,
    fecha_evento_inicio: Optional[str] = None,
    fecha_evento_fin: Optional[str] = None,
    puntos_asistencia: Optional[int] = 0
) -> Dict:
    """
    (SOLDADO DE CREACIÓN) Crea una nueva publicación (Noticia, Blog, Evento, Capacitación).
    `autor_id` es el ID del usuario que crea. `tipo` debe ser uno de: 'EVENTO', 'NOTICIA', 'BLOG', 'CAPACITACION'.
    Los campos de evento y capacitación son opcionales. `fecha_evento_inicio` y `fecha_evento_fin` deben estar en formato YYYY-MM-DD HH:MM:SS.
    La publicación se crea en estado 'BORRADOR'.
    """
    print(f"--- 💥 SOLDADO (Creación Contenido): ¡ACCIÓN! Creando publicación '{titulo}' de tipo {tipo}. ---")
    try:
        autor = CustomUser.objects.get(id=autor_id)

        if tipo not in Publicacion.Tipo.values:
            return {"status": "error", "message": f"Tipo de publicación inválido. Válidos: {Publicacion.Tipo.labels}"}

        # Generar slug único
        base_slug = slugify(titulo)
        slug = base_slug
        counter = 1
        while Publicacion.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        publicacion = Publicacion.objects.create(
            autor=autor,
            tipo=tipo,
            titulo=titulo,
            slug=slug,
            contenido=contenido,
            imagen_principal=imagen_principal_path,
            subcategoria_evento=subcategoria_evento,
            fecha_evento_inicio=datetime.fromisoformat(fecha_evento_inicio) if fecha_evento_inicio else None,
            fecha_evento_fin=datetime.fromisoformat(fecha_evento_fin) if fecha_evento_fin else None,
            puntos_asistencia=puntos_asistencia,
            estado=Publicacion.Status.BORRADOR
        )
        return {"status": "success", "publicacion_id": publicacion.id, "message": f"Publicación '{titulo}' creada como borrador."}
    except ObjectDoesNotExist:
        return {"status": "error", "message": f"El autor con ID {autor_id} no existe."}
    except Exception as e:
        return {"status": "error", "message": f"Ocurrió un error inesperado: {e}"}

@tool
def actualizar_publicacion(publicacion_id: int, **kwargs) -> Dict:
    """
    (SOLDADO DE EDICIÓN) Actualiza los campos de una publicación que está en estado 'BORRADOR'.
    Se pueden pasar como argumentos: titulo, contenido, imagen_principal_path, etc.
    """
    print(f"--- 💥 SOLDADO (Edición Contenido): ¡ACCIÓN! Actualizando publicación ID {publicacion_id}. ---")
    try:
        pub = Publicacion.objects.get(id=publicacion_id)
        if pub.estado != Publicacion.Status.BORRADOR:
            return {"status": "error", "message": f"Solo se pueden editar publicaciones en estado 'Borrador'. Estado actual: {pub.get_estado_display()}."}

        for key, value in kwargs.items():
            if hasattr(pub, key):
                if 'fecha' in key and value:
                    setattr(pub, key, datetime.fromisoformat(value))
                else:
                    setattr(pub, key, value)

        pub.save()
        return {"status": "success", "publicacion_id": pub.id, "message": "Publicación actualizada con éxito."}
    except ObjectDoesNotExist:
        return {"status": "error", "message": f"No se encontró una publicación con el ID {publicacion_id}."}

# --- SOLDADOS DE FLUJO DE APROBACIÓN ---

@tool
def gestionar_flujo_aprobacion_publicacion(publicacion_id: int, accion: str) -> Dict:
    """
    (SOLDADO DE FLUJO DE TRABAJO) Gestiona el ciclo de vida de una publicación.
    `accion` puede ser: 'ENVIAR_A_DIRECTIVO', 'APROBAR_DIRECTIVO', 'APROBAR_ADMIN', 'PUBLICAR', 'DEVOLVER_A_BORRADOR'.
    """
    print(f"--- 💥 SOLDADO (Flujo de Trabajo): ¡ACCIÓN! Ejecutando '{accion}' en publicación ID {publicacion_id}. ---")
    try:
        pub = Publicacion.objects.get(id=publicacion_id)
        estado_actual = pub.estado
        nuevo_estado = None

        if accion == 'ENVIAR_A_DIRECTIVO' and estado_actual == Publicacion.Status.BORRADOR:
            nuevo_estado = Publicacion.Status.PENDIENTE_DIRECTIVO
        elif accion == 'APROBAR_DIRECTIVO' and estado_actual == Publicacion.Status.PENDIENTE_DIRECTIVO:
            nuevo_estado = Publicacion.Status.PENDIENTE_ADMIN
        elif accion == 'APROBAR_ADMIN' and estado_actual == Publicacion.Status.PENDIENTE_ADMIN:
            nuevo_estado = Publicacion.Status.PUBLICADO
        elif accion == 'PUBLICAR' and estado_actual in [Publicacion.Status.BORRADOR, Publicacion.Status.PENDIENTE_ADMIN]:
            # Asumimos que un admin puede publicar directamente
            nuevo_estado = Publicacion.Status.PUBLICADO
        elif accion == 'DEVOLVER_A_BORRADOR' and estado_actual != Publicacion.Status.PUBLICADO:
            nuevo_estado = Publicacion.Status.BORRADOR
        else:
            return {"status": "error", "message": f"La acción '{accion}' no es válida para el estado actual '{pub.get_estado_display()}'."}

        pub.estado = nuevo_estado
        pub.save(update_fields=['estado'])
        return {"status": "success", "message": f"El estado de la publicación ha sido actualizado a '{pub.get_estado_display()}'."}
    except ObjectDoesNotExist:
        return {"status": "error", "message": f"No se encontró una publicación con el ID {publicacion_id}."}

# --- SOLDADOS DE CONSULTA Y ELIMINACIÓN ---

@tool
def consultar_publicacion_por_id(publicacion_id: int) -> Dict:
    """
    (SOLDADO DE RECONOCIMIENTO) Busca y devuelve los datos detallados de una publicación por su ID.
    """
    print(f"--- 💥 SOLDADO (Reconocimiento Contenido): ¡ACCIÓN! Buscando publicación ID {publicacion_id}. ---")
    try:
        pub = Publicacion.objects.select_related('autor').get(id=publicacion_id)
        datos = {
            "id": pub.id,
            "titulo": pub.titulo,
            "tipo": pub.get_tipo_display(),
            "estado": pub.get_estado_display(),
            "autor": pub.autor.username if pub.autor else "N/A",
            "contenido": pub.contenido[:200] + "...", # Snippet
            "fecha_publicacion": pub.fecha_publicacion.isoformat(),
            "fecha_evento_inicio": pub.fecha_evento_inicio.isoformat() if pub.fecha_evento_inicio else None,
            "fecha_evento_fin": pub.fecha_evento_fin.isoformat() if pub.fecha_evento_fin else None,
            "puntos_asistencia": pub.puntos_asistencia
        }
        return {"status": "success", "data": datos}
    except ObjectDoesNotExist:
        return {"status": "error", "message": f"No se encontró una publicación con el ID {publicacion_id}."}

@tool
def listar_publicaciones(tipo: Optional[str] = None, estado: Optional[str] = None) -> Dict:
    """
    (SOLDADO DE PATRULLA) Devuelve una lista de publicaciones, con filtros opcionales por tipo y estado.
    `tipo` puede ser: 'EVENTO', 'NOTICIA', 'BLOG', 'CAPACITACION'.
    `estado` puede ser: 'BORRADOR', 'PENDIENTE_DIRECTIVO', 'PENDIENTE_ADMIN', 'PUBLICADO'.
    """
    print(f"--- 💥 SOLDADO (Patrulla Contenido): ¡ACCIÓN! Listando publicaciones... ---")
    try:
        query = Publicacion.objects.all()
        if tipo:
            if tipo not in Publicacion.Tipo.values:
                return {"status": "error", "message": f"Tipo inválido. Válidos: {Publicacion.Tipo.labels}"}
            query = query.filter(tipo=tipo)
        if estado:
            if estado not in Publicacion.Status.values:
                return {"status": "error", "message": f"Estado inválido. Válidos: {Publicacion.Status.labels}"}
            query = query.filter(estado=estado)

        publicaciones = query.order_by('-fecha_publicacion')
        lista = [{"id": p.id, "titulo": p.titulo, "tipo": p.get_tipo_display(), "estado": p.get_estado_display()} for p in publicaciones]

        return {"status": "success", "count": len(lista), "publicaciones": lista}
    except Exception as e:
        return {"status": "error", "message": f"Ocurrió un error inesperado al listar: {e}"}

@tool
def eliminar_publicacion(publicacion_id: int) -> Dict:
    """
    (SOLDADO DE ELIMINACIÓN) Elimina una publicación de la base de datos.
    Se recomienda usar con precaución.
    """
    print(f"--- 💥 SOLDADO (Eliminación Contenido): ¡ACCIÓN! Eliminando publicación ID {publicacion_id}. ---")
    try:
        pub = Publicacion.objects.get(id=publicacion_id)
        titulo = pub.titulo
        pub.delete()
        return {"status": "success", "message": f"La publicación '{titulo}' ha sido eliminada permanentemente."}
    except ObjectDoesNotExist:
        return {"status": "error", "message": f"No se encontró una publicación con el ID {publicacion_id}."}

def get_publicaciones_soldiers() -> List:
    """ Recluta y devuelve la Escuadra de Publicaciones completa. """
    return [
        crear_publicacion,
        actualizar_publicacion,
        gestionar_flujo_aprobacion_publicacion,
        consultar_publicacion_por_id,
        listar_publicaciones,
        eliminar_publicacion,
    ]