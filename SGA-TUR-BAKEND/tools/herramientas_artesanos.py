# from langchain_core.tools import tool
from typing import List, Dict, Optional
from api.models import (
    CustomUser,
    RubroArtesano,
    Artesano,
    ImagenArtesano
)
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.utils.text import slugify

# --- SOLDADOS DE GESTIÓN DE PERFILES (CRUD) ---

@tool
def crear_perfil_artesano(email: str, nombre_taller: str, nombre_artesano: str, rubro_slug: str, telefono: str) -> Dict:
    """
    (SOLDADO DE REGISTRO) Ejecuta la creación de un nuevo usuario de tipo ARTESANO y su perfil asociado.
    Requiere un email único, nombre del taller, nombre del artesano, el slug del rubro (ej. 'tejidos', 'ceramica') y un teléfono.
    El perfil se crea como 'no aprobado' por defecto. Devuelve el ID del nuevo artesano.
    """
    print(f"--- 💥 SOLDADO (Registro Artesano): ¡ACCIÓN! Creando perfil para '{nombre_taller}' con email {email}. ---")
    try:
        if CustomUser.objects.filter(email=email).exists():
            return {"status": "error", "message": f"El email {email} ya está en uso."}

        rubro = RubroArtesano.objects.get(slug=rubro_slug)

        user = CustomUser.objects.create_user(
            username=email,
            email=email,
            role=CustomUser.Role.ARTESANO
        )
        user.set_password(f"temp_art_{slugify(nombre_taller)}_{user.id}") # Contraseña temporal
        user.save()

        artesano = Artesano.objects.create(
            usuario=user,
            nombre_taller=nombre_taller,
            nombre_artesano=nombre_artesano,
            rubro=rubro,
            telefono=telefono,
            aprobado=False
        )
        return {"status": "success", "artesano_id": artesano.id, "message": f"Usuario y perfil para '{nombre_taller}' creados. El perfil está pendiente de aprobación."}
    except ObjectDoesNotExist:
        return {"status": "error", "message": f"El rubro con slug '{rubro_slug}' no existe."}
    except IntegrityError as e:
        return {"status": "error", "message": f"Error de integridad de datos: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"Ocurrió un error inesperado: {e}"}

@tool
def actualizar_perfil_artesano(
    artesano_id: int,
    nombre_taller: Optional[str] = None,
    nombre_artesano: Optional[str] = None,
    descripcion: Optional[str] = None,
    telefono: Optional[str] = None,
    email_contacto: Optional[str] = None,
    facebook_url: Optional[str] = None,
    instagram_url: Optional[str] = None,
    tiktok_url: Optional[str] = None,
    whatsapp: Optional[str] = None,
    direccion: Optional[str] = None,
    latitud: Optional[float] = None,
    longitud: Optional[float] = None
) -> Dict:
    """
    (SOLDADO DE ACTUALIZACIÓN) Ejecuta la actualización de los datos de un perfil de artesano existente.
    Permite modificar múltiples campos a la vez. Los campos no proporcionados no se modificarán.
    """
    print(f"--- 💥 SOLDADO (Actualización Artesano): ¡ACCIÓN! Actualizando datos para el artesano_id {artesano_id}. ---")
    try:
        artesano = Artesano.objects.get(id=artesano_id)
        update_fields = []

        if nombre_taller: artesano.nombre_taller = nombre_taller; update_fields.append('nombre_taller')
        if nombre_artesano: artesano.nombre_artesano = nombre_artesano; update_fields.append('nombre_artesano')
        if descripcion: artesano.descripcion = descripcion; update_fields.append('descripcion')
        if telefono: artesano.telefono = telefono; update_fields.append('telefono')
        if email_contacto: artesano.email_contacto = email_contacto; update_fields.append('email_contacto')
        if facebook_url: artesano.red_social_facebook = facebook_url; update_fields.append('red_social_facebook')
        if instagram_url: artesano.red_social_instagram = instagram_url; update_fields.append('red_social_instagram')
        if tiktok_url: artesano.red_social_tiktok = tiktok_url; update_fields.append('red_social_tiktok')
        if whatsapp: artesano.red_social_whatsapp = whatsapp; update_fields.append('red_social_whatsapp')
        if direccion: artesano.direccion = direccion; update_fields.append('direccion')
        if latitud is not None: artesano.latitud = latitud; update_fields.append('latitud')
        if longitud is not None: artesano.longitud = longitud; update_fields.append('longitud')

        if not update_fields:
            return {"status": "info", "message": "No se proporcionaron campos para actualizar."}

        artesano.save(update_fields=update_fields)
        return {"status": "success", "artesano_id": artesano.id, "message": f"Datos del artesano actualizados correctamente. Campos modificados: {', '.join(update_fields)}."}
    except ObjectDoesNotExist:
        return {"status": "error", "message": f"No se encontró un artesano con el ID {artesano_id}."}
    except Exception as e:
        return {"status": "error", "message": f"Ocurrió un error inesperado al actualizar: {e}"}

@tool
def gestionar_aprobacion_artesano(artesano_id: int, aprobar: bool) -> Dict:
    """
    (SOLDADO DE COMANDO) Aprueba o desaprueba el perfil de un artesano para que sea visible públicamente.
    `aprobar` debe ser True para aprobar o False para desaprobar.
    """
    print(f"--- 💥 SOLDADO (Comando Artesano): ¡ACCIÓN! {'Aprobando' if aprobar else 'Desaprobando'} al artesano_id {artesano_id}. ---")
    try:
        artesano = Artesano.objects.get(id=artesano_id)
        artesano.aprobado = aprobar
        artesano.save(update_fields=['aprobado'])
        estado = "aprobado" if aprobar else "desaprobado"
        return {"status": "success", "message": f"El perfil del artesano '{artesano.nombre_taller}' ha sido {estado}."}
    except ObjectDoesNotExist:
        return {"status": "error", "message": f"No se encontró un artesano con el ID {artesano_id}."}

# --- SOLDADOS DE GESTIÓN DE GALERÍA ---

@tool
def establecer_foto_principal_artesano(artesano_id: int, ruta_archivo_imagen: str) -> Dict:
    """
    (SOLDADO DE IMAGEN) Establece o actualiza la foto principal de un artesano.
    `ruta_archivo_imagen` es la ruta a un archivo en el sistema de almacenamiento.
    """
    print(f"--- 💥 SOLDADO (Imagen Artesano): ¡ACCIÓN! Estableciendo foto principal para el artesano_id {artesano_id}. ---")
    try:
        artesano = Artesano.objects.get(id=artesano_id)
        artesano.foto_principal.name = ruta_archivo_imagen
        artesano.save(update_fields=['foto_principal'])
        return {"status": "success", "message": f"Foto principal para '{artesano.nombre_taller}' actualizada."}
    except ObjectDoesNotExist:
        return {"status": "error", "message": f"No se encontró un artesano con el ID {artesano_id}."}

@tool
def agregar_foto_galeria_artesano(artesano_id: int, ruta_archivo_imagen: str, alt_text: str) -> Dict:
    """
    (SOLDADO DE GALERÍA) Añade una nueva imagen a la galería de un artesano.
    `ruta_archivo_imagen` es la ruta a un archivo en el sistema de almacenamiento.
    """
    print(f"--- 💥 SOLDADO (Galería Artesano): ¡ACCIÓN! Agregando imagen a la galería del artesano_id {artesano_id}. ---")
    try:
        artesano = Artesano.objects.get(id=artesano_id)
        imagen = ImagenArtesano.objects.create(
            artesano=artesano,
            imagen=ruta_archivo_imagen,
            alt_text=alt_text
        )
        return {"status": "success", "image_id": imagen.id, "message": "Imagen añadida a la galería con éxito."}
    except ObjectDoesNotExist:
        return {"status": "error", "message": f"No se encontró un artesano con el ID {artesano_id}."}

@tool
def eliminar_foto_galeria_artesano(imagen_id: int) -> Dict:
    """
    (SOLDADO DE GALERÍA) Elimina una imagen de la galería de un artesano por su ID.
    NOTA: Esto solo elimina el registro de la base de datos, no el archivo físico.
    """
    print(f"--- 💥 SOLDADO (Galería Artesano): ¡ACCIÓN! Eliminando imagen_id {imagen_id} de la galería. ---")
    try:
        imagen = ImagenArtesano.objects.get(id=imagen_id)
        artesano_nombre = imagen.artesano.nombre_taller
        imagen.delete()
        return {"status": "success", "message": f"Imagen eliminada de la galería de '{artesano_nombre}'."}
    except ObjectDoesNotExist:
        return {"status": "error", "message": f"No se encontró una imagen de artesano con el ID {imagen_id}."}

# --- SOLDADOS DE CONSULTA ---

@tool
def consultar_artesano_por_id(artesano_id: int) -> Dict:
    """
    (SOLDADO DE RECONOCIMIENTO) Busca y devuelve los datos detallados de un artesano por su ID.
    """
    print(f"--- 💥 SOLDADO (Reconocimiento Artesano): ¡ACCIÓN! Buscando al artesano con ID {artesano_id}. ---")
    try:
        artesano = Artesano.objects.select_related('usuario', 'rubro').get(id=artesano_id)
        datos = {
            "id": artesano.id,
            "nombre_taller": artesano.nombre_taller,
            "nombre_artesano": artesano.nombre_artesano,
            "descripcion": artesano.descripcion,
            "telefono": artesano.telefono,
            "email_usuario": artesano.usuario.email,
            "email_contacto": artesano.email_contacto,
            "rubro": artesano.rubro.nombre,
            "aprobado": artesano.aprobado,
            "ubicacion": {
                "direccion": artesano.direccion,
                "latitud": artesano.latitud,
                "longitud": artesano.longitud
            },
            "puntuacion": {
                "capacitacion": artesano.puntuacion_capacitacion,
                "reseñas": artesano.puntuacion_reseñas,
                "total": artesano.puntuacion_total
            }
        }
        return {"status": "success", "data": datos}
    except ObjectDoesNotExist:
        return {"status": "error", "message": f"No se encontró ningún artesano con el ID {artesano_id}."}

@tool
def listar_artesanos_por_rubro(rubro_slug: str, solo_aprobados: bool = True) -> Dict:
    """
    (SOLDADO DE PATRULLA) Devuelve una lista de los artesanos que pertenecen a un rubro.
    Por defecto, lista solo los aprobados.
    """
    print(f"--- 💥 SOLDADO (Patrulla Artesano): ¡ACCIÓN! Listando artesanos del rubro '{rubro_slug}'. ---")
    try:
        artesanos = Artesano.objects.filter(rubro__slug=rubro_slug)
        if solo_aprobados:
            artesanos = artesanos.filter(aprobado=True)

        if not artesanos.exists():
            return {"status": "success", "message": f"No se encontraron artesanos en el rubro '{rubro_slug}'."}

        lista_artesanos = [{"id": a.id, "nombre_taller": a.nombre_taller, "nombre_artesano": a.nombre_artesano, "puntuacion": a.puntuacion_total} for a in artesanos]
        return {"status": "success", "rubro_slug": rubro_slug, "artesanos": lista_artesanos}
    except Exception as e:
        return {"status": "error", "message": f"Ocurrió un error inesperado al listar: {e}"}


def get_artesano_soldiers() -> List:
    """ Recluta y devuelve la Escuadra de Artesanos completa. """
    return [
        crear_perfil_artesano,
        actualizar_perfil_artesano,
        gestionar_aprobacion_artesano,
        establecer_foto_principal_artesano,
        agregar_foto_galeria_artesano,
        eliminar_foto_galeria_artesano,
        consultar_artesano_por_id,
        listar_artesanos_por_rubro,
    ]