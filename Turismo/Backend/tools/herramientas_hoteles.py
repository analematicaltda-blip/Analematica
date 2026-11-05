# from langchain_core.tools import tool
from typing import List, Dict
# from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.models.perfil import Perfil as PrestadorServicio
from apps.prestadores.models import Perfil as PrestadorServicio
from apps.turismo.models import Hotel
from django.core.exceptions import ObjectDoesNotExist

@tool
def actualizar_detalles_hotel(prestador_id: int, ocupacion_nacional: int, ocupacion_internacional: int) -> Dict:
    """
    (SOLDADO ESPECIALISTA EN HOTELES) Actualiza los detalles específicos para un prestador de tipo hotel,
    como los reportes de ocupación. Si los detalles no existen, los crea.
    """
    print(f"--- 💥 SOLDADO (Hoteles): ¡ACCIÓN! Actualizando detalles para el prestador_id {prestador_id}. ---")
    try:
        prestador = PrestadorServicio.objects.get(id=prestador_id)
        if prestador.categoria.slug != 'hoteles':
            return {"status": "error", "message": "Esta operación solo es válida para prestadores de la categoría 'hoteles'."}

        hotel, created = Hotel.objects.get_or_create(prestador=prestador)
        hotel.reporte_ocupacion_nacional = ocupacion_nacional
        hotel.reporte_ocupacion_internacional = ocupacion_internacional
        hotel.save()

        accion = "creados" if created else "actualizados"
        return {"status": "success", "message": f"Detalles de hotel para '{prestador.nombre_negocio}' {accion} correctamente."}
    except ObjectDoesNotExist:
        return {"status": "error", "message": f"No se encontró un prestador con el ID {prestador_id}."}
    except Exception as e:
        return {"status": "error", "message": f"Ocurrió un error inesperado: {e}"}


def get_hoteles_soldiers() -> List:
    """
    Recluta y devuelve la Escuadra especialista de Hoteles.
    """
    return [
        actualizar_detalles_hotel,
    ]