# from langchain_core.tools import tool
# from typing import List, Dict, Optional
# from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.models.perfil import Perfil as PrestadorServicio
# from api.models import (
#     CustomUser,
#     CategoriaPrestador,
#     ImagenGaleria,
#     TipoDocumentoVerificacion,
#     DocumentoVerificacion
# )
# from apps.turismo.models import Hotel
from django.core.exceptions import ObjectDoesNotExist
# from django.db import IntegrityError
# from django.utils.text import slugify
# import os

# # --- SOLDADOS DE GESTIÓN DE PERFILES (CRUD) ---

# @tool
# def crear_perfil_prestador(email: str, nombre_negocio: str, categoria_slug: str, telefono: str) -> Dict:
#     """
#     (SOLDADO DE REGISTRO) Ejecuta la creación de un nuevo usuario de tipo PRESTADOR y su perfil de servicio asociado.
#     Requiere un email único para el usuario, el nombre del negocio, el slug de la categoría (ej. 'hoteles', 'restaurantes') y un teléfono.
#     El perfil se crea como 'no aprobado' por defecto. Devuelve el ID del nuevo prestador.
#     """
#     print(f"--- 💥 SOLDADO (Registro): ¡ACCIÓN! Creando perfil para '{nombre_negocio}' con email {email}. ---")
#     try:
#         if CustomUser.objects.filter(email=email).exists():
#             return {"status": "error", "message": f"El email {email} ya está en uso."}

#         categoria = CategoriaPrestador.objects.get(slug=categoria_slug)

#         user = CustomUser.objects.create_user(
#             username=email,
#             email=email,
#             role=CustomUser.Role.PRESTADOR
#         )
#         user.set_password(f"temp_{slugify(nombre_negocio)}_{user.id}") # Contraseña temporal
#         user.save()

#         prestador = PrestadorServicio.objects.create(
#             usuario=user,
#             nombre_comercial=nombre_negocio, # Corregido a 'nombre_comercial'
#             categoria=categoria,
#             telefono_principal=telefono, # Corregido a 'telefono_principal'
#             estado='Pendiente' # Corregido a 'estado'
#         )
#         return {"status": "success", "prestador_id": prestador.id, "message": f"Usuario y perfil para '{nombre_negocio}' creados. El perfil está pendiente de aprobación."}
#     except ObjectDoesNotExist:
#         return {"status": "error", "message": f"La categoría con slug '{categoria_slug}' no existe."}
#     except IntegrityError as e:
#         return {"status": "error", "message": f"Error de integridad de datos: {e}"}
#     except Exception as e:
#         return {"status": "error", "message": f"Ocurrió un error inesperado: {e}"}

# @tool
# def actualizar_perfil_prestador(
#     prestador_id: int,
#     nombre_negocio: Optional[str] = None,
#     descripcion: Optional[str] = None,
#     telefono: Optional[str] = None,
#     email_contacto: Optional[str] = None,
#     facebook_url: Optional[str] = None,
#     instagram_url: Optional[str] = None,
#     tiktok_url: Optional[str] = None,
#     whatsapp: Optional[str] = None,
#     direccion: Optional[str] = None,
#     latitud: Optional[float] = None,
#     longitud: Optional[float] = None,
#     promociones: Optional[str] = None
# ) -> Dict:
#     """
#     (SOLDADO DE ACTUALIZACIÓN) Ejecuta la actualización de los datos de un perfil de prestador de servicios existente.
#     Permite modificar múltiples campos a la vez. Los campos no proporcionados no se modificarán.
#     """
#     print(f"--- 💥 SOLDADO (Actualización): ¡ACCIÓN! Actualizando datos para el prestador_id {prestador_id}. ---")
#     try:
#         prestador = PrestadorServicio.objects.get(id=prestador_id)
#         update_fields = []

#         if nombre_negocio: prestador.nombre_comercial = nombre_negocio; update_fields.append('nombre_comercial')
#         if descripcion: prestador.descripcion_corta = descripcion; update_fields.append('descripcion_corta')
#         if telefono: prestador.telefono_principal = telefono; update_fields.append('telefono_principal')
#         if email_contacto: prestador.email_comercial = email_contacto; update_fields.append('email_comercial')
#         if facebook_url: prestador.sitio_web = facebook_url; update_fields.append('sitio_web') # Campo genérico
#         # Instagram, TikTok, WhatsApp no tienen campos directos en el nuevo modelo 'Perfil'

#         if direccion: prestador.direccion = direccion; update_fields.append('direccion')
#         if latitud is not None: prestador.latitud = latitud; update_fields.append('latitud')
#         if longitud is not None: prestador.longitud = longitud; update_fields.append('longitud')
#         # 'promociones' no tiene un campo directo en el nuevo modelo 'Perfil'

#         if not update_fields:
#             return {"status": "info", "message": "No se proporcionaron campos para actualizar."}

#         prestador.save(update_fields=update_fields)
#         return {"status": "success", "prestador_id": prestador.id, "message": f"Datos del negocio actualizados correctamente. Campos modificados: {', '.join(update_fields)}."}
#     except ObjectDoesNotExist:
#         return {"status": "error", "message": f"No se encontró un prestador con el ID {prestador_id}."}
#     except Exception as e:
#         return {"status": "error", "message": f"Ocurrió un error inesperado al actualizar: {e}"}

# @tool
# def gestionar_aprobacion_prestador(prestador_id: int, aprobar: bool) -> Dict:
#     """
#     (SOLDADO DE COMANDO) Aprueba o desaprueba el perfil de un prestador de servicios para que sea visible públicamente.
#     `aprobar` debe ser True para aprobar o False para desaprobar.
#     """
#     print(f"--- 💥 SOLDADO (Comando): ¡ACCIÓN! {'Aprobando' if aprobar else 'Rechazando'} al prestador_id {prestador_id}. ---")
#     try:
#         prestador = PrestadorServicio.objects.get(id=prestador_id)
#         prestador.estado = 'Activo' if aprobar else 'Rechazado'
#         prestador.save(update_fields=['estado'])
#         estado = "aprobado" if aprobar else "rechazado"
#         return {"status": "success", "message": f"El perfil del prestador '{prestador.nombre_comercial}' ha sido {estado}."}
#     except ObjectDoesNotExist:
#         return {"status": "error", "message": f"No se encontró un prestador con el ID {prestador_id}."}

# # --- SOLDADOS DE GESTIÓN DE ENTIDADES RELACIONADAS (Simplificado) ---

# # Nota: La gestión de galería y documentos se haría ahora a través de sus propios ViewSets/herramientas,
# # pero se mantiene una función de consulta para demostrar la relación.

# @tool
# def consultar_prestador_por_id(prestador_id: int) -> Dict:
#     """
#     (SOLDADO DE RECONOCIMIENTO) Busca y devuelve los datos detallados de un prestador de servicios por su ID.
#     """
#     print(f"--- 💥 SOLDADO (Reconocimiento): ¡ACCIÓN! Buscando al prestador con ID {prestador_id}. ---")
#     try:
#         prestador = PrestadorServicio.objects.select_related('usuario', 'categoria').get(id=prestador_id)
#         datos = {
#             "id": prestador.id,
#             "nombre_negocio": prestador.nombre_comercial,
#             "descripcion": prestador.descripcion_corta,
#             "telefono": prestador.telefono_principal,
#             "email_usuario": prestador.usuario.email,
#             "email_contacto": prestador.email_comercial,
#             "categoria": prestador.categoria.nombre,
#             "estado": prestador.get_estado_display(),
#             "ubicacion": {
#                 "direccion": prestador.direccion,
#                 "latitud": prestador.latitud,
#                 "longitud": prestador.longitud
#             },
#         }
#         return {"status": "success", "data": datos}
#     except ObjectDoesNotExist:
#         return {"status": "error", "message": f"No se encontró ningún prestador con el ID {prestador_id}."}
#     except Exception as e:
#         return {"status": "error", "message": f"Ocurrió un error inesperado al consultar: {e}"}

# @tool
# def listar_prestadores_por_categoria(categoria_slug: str, solo_activos: bool = True) -> Dict:
#     """
#     (SOLDADO DE PATRULLA) Devuelve una lista de los prestadores de servicios que pertenecen a una categoría.
#     Por defecto, lista solo los activos.
#     """
#     print(f"--- 💥 SOLDADO (Patrulla): ¡ACCIÓN! Listando prestadores de la categoría '{categoria_slug}'. ---")
#     try:
#         prestadores = PrestadorServicio.objects.filter(categoria__slug=categoria_slug)
#         if solo_activos:
#             prestadores = prestadores.filter(estado='Activo')

#         if not prestadores.exists():
#             return {"status": "success", "message": f"No se encontraron prestadores en la categoría '{categoria_slug}'."}

#         lista_prestadores = [{"id": p.id, "nombre": p.nombre_comercial} for p in prestadores]
#         return {"status": "success", "categoria_slug": categoria_slug, "prestadores": lista_prestadores}
#     except Exception as e:
#         return {"status": "error", "message": f"Ocurrió un error inesperado al listar: {e}"}


def get_prestador_soldiers() -> list:
    """ Recluta y devuelve la Escuadra de Prestadores completa. """
    return [
        # crear_perfil_prestador,
        # actualizar_perfil_prestador,
        # gestionar_aprobacion_prestador,
        # consultar_prestador_por_id,
        # listar_prestadores_por_categoria,
    ]
