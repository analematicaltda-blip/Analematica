# from langchain_core.tools import tool
from typing import List, Dict, Optional
from api.models import AtractivoTuristico, ImagenAtractivo, CustomUser
from django.core.exceptions import ObjectDoesNotExist
from django.utils.text import slugify

# --- SOLDADOS DE GESTIÓN DE ATRACTIVOS (CRUD) ---

@tool
def crear_atractivo_turistico(
    autor_id: int,
    nombre: str,
    descripcion: str,
    categoria_color: str,
    como_llegar: str,
    direccion: str,
    latitud: float,
    longitud: float
) -> Dict:
    """
    (SOLDADO DE INVENTARIO) Registra un nuevo atractivo turístico.
    Requiere el ID del autor, nombre, descripción, categoría de color ('AMARILLO', 'ROJO', 'BLANCO'),
    instrucciones de cómo llegar y la ubicación (dirección y coordenadas).
    El atractivo se crea como 'no publicado' por defecto.
    """
    print(f"--- 💥 SOLDADO (Inventario Atractivos): ¡ACCIÓN! Creando atractivo '{nombre}'. ---")
    try:
        autor = CustomUser.objects.get(id=autor_id)
        if categoria_color not in AtractivoTuristico.CategoriaColor.values:
            return {"status": "error", "message": f"Categoría de color inválida. Válidas: {AtractivoTuristico.CategoriaColor.labels}"}

        base_slug = slugify(nombre)
        slug = base_slug
        counter = 1
        while AtractivoTuristico.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        atractivo = AtractivoTuristico.objects.create(
            autor=autor,
            nombre=nombre,
            slug=slug,
            descripcion=descripcion,
            categoria_color=categoria_color,
            como_llegar=como_llegar,
            direccion=direccion,
            latitud=latitud,
            longitud=longitud,
            es_publicado=False
        )
        return {"status": "success", "atractivo_id": atractivo.id, "message": f"Atractivo '{nombre}' creado con éxito. Pendiente de publicación."}
    except ObjectDoesNotExist:
        return {"status": "error", "message": f"El autor con ID {autor_id} no existe."}
    except Exception as e:
        return {"status": "error", "message": f"Ocurrió un error inesperado: {e}"}

@tool
def actualizar_atractivo_turistico(atractivo_id: int, **kwargs) -> Dict:
    """
    (SOLDADO DE EDICIÓN) Actualiza los campos de un atractivo turístico existente.
    Se pueden pasar como argumentos opcionales: nombre, descripcion, como_llegar, horario_funcionamiento, tarifas, recomendaciones, accesibilidad, etc.
    """
    print(f"--- 💥 SOLDADO (Edición Atractivos): ¡ACCIÓN! Actualizando atractivo ID {atractivo_id}. ---")
    try:
        atractivo = AtractivoTuristico.objects.get(id=atractivo_id)
        for key, value in kwargs.items():
            if hasattr(atractivo, key):
                setattr(atractivo, key, value)

        atractivo.save()
        return {"status": "success", "atractivo_id": atractivo.id, "message": "Atractivo turístico actualizado con éxito."}
    except ObjectDoesNotExist:
        return {"status": "error", "message": f"No se encontró un atractivo con el ID {atractivo_id}."}

@tool
def gestionar_publicacion_atractivo(atractivo_id: int, publicar: bool) -> Dict:
    """
    (SOLDADO DE COMANDO) Publica o despublica un atractivo turístico para que sea visible en el sitio web.
    `publicar` debe ser True para publicar o False para ocultar.
    """
    print(f"--- 💥 SOLDADO (Comando Atractivos): ¡ACCIÓN! {'Publicando' if publicar else 'Ocultando'} el atractivo ID {atractivo_id}. ---")
    try:
        atractivo = AtractivoTuristico.objects.get(id=atractivo_id)
        atractivo.es_publicado = publicar
        atractivo.save(update_fields=['es_publicado'])
        estado = "publicado" if publicar else "ocultado"
        return {"status": "success", "message": f"El atractivo '{atractivo.nombre}' ha sido {estado}."}
    except ObjectDoesNotExist:
        return {"status": "error", "message": f"No se encontró un atractivo con el ID {atractivo_id}."}

# --- SOLDADOS DE GESTIÓN DE GALERÍA ---

@tool
def establecer_imagen_principal_atractivo(atractivo_id: int, ruta_archivo_imagen: str) -> Dict:
    """
    (SOLDADO DE IMAGEN) Establece o actualiza la imagen principal de un atractivo.
    `ruta_archivo_imagen` es la ruta a un archivo en el sistema de almacenamiento.
    """
    print(f"--- 💥 SOLDADO (Imagen Atractivo): ¡ACCIÓN! Estableciendo imagen principal para el atractivo ID {atractivo_id}. ---")
    try:
        atractivo = AtractivoTuristico.objects.get(id=atractivo_id)
        atractivo.imagen_principal.name = ruta_archivo_imagen
        atractivo.save(update_fields=['imagen_principal'])
        return {"status": "success", "message": f"Imagen principal para '{atractivo.nombre}' actualizada."}
    except ObjectDoesNotExist:
        return {"status": "error", "message": f"No se encontró un atractivo con el ID {atractivo_id}."}

@tool
def agregar_imagen_galeria_atractivo(atractivo_id: int, ruta_archivo_imagen: str, alt_text: str) -> Dict:
    """
    (SOLDADO DE GALERÍA) Añade una nueva imagen a la galería de un atractivo.
    `ruta_archivo_imagen` es la ruta a un archivo en el sistema de almacenamiento.
    """
    print(f"--- 💥 SOLDADO (Galería Atractivo): ¡ACCIÓN! Agregando imagen a la galería del atractivo ID {atractivo_id}. ---")
    try:
        atractivo = AtractivoTuristico.objects.get(id=atractivo_id)
        imagen = ImagenAtractivo.objects.create(
            atractivo=atractivo,
            imagen=ruta_archivo_imagen,
            alt_text=alt_text
        )
        return {"status": "success", "image_id": imagen.id, "message": "Imagen añadida a la galería con éxito."}
    except ObjectDoesNotExist:
        return {"status": "error", "message": f"No se encontró un atractivo con el ID {atractivo_id}."}

@tool
def eliminar_imagen_galeria_atractivo(imagen_id: int) -> Dict:
    """
    (SOLDADO DE GALERÍA) Elimina una imagen de la galería de un atractivo por su ID.
    NOTA: Esto solo elimina el registro de la base de datos, no el archivo físico.
    """
    print(f"--- 💥 SOLDADO (Galería Atractivo): ¡ACCIÓN! Eliminando imagen_id {imagen_id} de la galería. ---")
    try:
        imagen = ImagenAtractivo.objects.get(id=imagen_id)
        atractivo_nombre = imagen.atractivo.nombre
        imagen.delete()
        return {"status": "success", "message": f"Imagen eliminada de la galería de '{atractivo_nombre}'."}
    except ObjectDoesNotExist:
        return {"status": "error", "message": f"No se encontró una imagen de atractivo con el ID {imagen_id}."}

# --- SOLDADOS DE CONSULTA ---

@tool
def consultar_atractivo_por_id(atractivo_id: int) -> Dict:
    """
    (SOLDADO DE RECONOCIMIENTO) Busca y devuelve los datos detallados de un atractivo turístico por su ID.
    """
    print(f"--- 💥 SOLDADO (Reconocimiento Atractivos): ¡ACCIÓN! Buscando atractivo ID {atractivo_id}. ---")
    try:
        atractivo = AtractivoTuristico.objects.get(id=atractivo_id)
        datos = {
            "id": atractivo.id,
            "nombre": atractivo.nombre,
            "descripcion": atractivo.descripcion,
            "categoria": atractivo.get_categoria_color_display(),
            "publicado": atractivo.es_publicado,
            "ubicacion": {
                "direccion": atractivo.direccion,
                "latitud": atractivo.latitud,
                "longitud": atractivo.longitud
            },
            "detalles": {
                "como_llegar": atractivo.como_llegar,
                "horario": atractivo.horario_funcionamiento,
                "tarifas": atractivo.tarifas,
                "recomendaciones": atractivo.recomendaciones,
                "accesibilidad": atractivo.accesibilidad
            }
        }
        return {"status": "success", "data": datos}
    except ObjectDoesNotExist:
        return {"status": "error", "message": f"No se encontró un atractivo con el ID {atractivo_id}."}

@tool
def listar_atractivos(categoria_color: Optional[str] = None, solo_publicados: bool = True) -> Dict:
    """
    (SOLDADO DE PATRULLA) Devuelve una lista de atractivos, con filtros opcionales por categoría de color y estado de publicación.
    """
    print(f"--- 💥 SOLDADO (Patrulla Atractivos): ¡ACCIÓN! Listando atractivos... ---")
    try:
        query = AtractivoTuristico.objects.all()
        if categoria_color:
            query = query.filter(categoria_color=categoria_color)
        if solo_publicados:
            query = query.filter(es_publicado=True)

        atractivos = query.order_by('nombre')
        lista = [{"id": a.id, "nombre": a.nombre, "categoria": a.get_categoria_color_display()} for a in atractivos]

        return {"status": "success", "count": len(lista), "atractivos": lista}
    except Exception as e:
        return {"status": "error", "message": f"Ocurrió un error inesperado al listar: {e}"}


def get_atractivos_soldiers() -> List:
    """ Recluta y devuelve la Escuadra de Atractivos Turísticos completa. """
    return [
        crear_atractivo_turistico,
        actualizar_atractivo_turistico,
        gestionar_publicacion_atractivo,
        establecer_imagen_principal_atractivo,
        agregar_imagen_galeria_atractivo,
        eliminar_imagen_galeria_atractivo,
        consultar_atractivo_por_id,
        listar_atractivos,
    ]