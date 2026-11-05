import math
import logging
from ..models import ServiceLocation
from .notification_service import send_push_notification

logger = logging.getLogger(__name__)

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Fórmula de Haversine para calcular la distancia entre dos coordenadas en km.
    """
    R = 6371  # Radio de la Tierra en kilómetros
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2)**2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def detect_nearby_tourists(tourist_lat, tourist_lon, tourist_user):
    """
    Hallazgo 11: Geofencing para prestadores.
    Compara la ubicación del turista con las geocercas activas de los prestadores.
    """
    active_geofences = ServiceLocation.objects.filter(is_active=True)
    matches = []

    for geofence in active_geofences:
        distance_km = haversine_distance(tourist_lat, tourist_lon, geofence.latitude, geofence.longitude)
        distance_m = distance_km * 1000

        if distance_m <= geofence.radius:
            logger.info(f"SARITA Geofence: Alerta detectada para prestador {geofence.provider.email} (Distancia: {distance_m:.1f}m)")

            # Notificar al prestador sobre el turista cercano
            send_push_notification(
                user_id=geofence.provider.id,
                title="¡Turista cercano detectado!",
                message=f"Hay un cliente potencial a {int(distance_m)} metros de tu ubicación.",
                data={"event": "geofence_match", "tourist_id": str(tourist_user.id)}
            )
            matches.append(geofence)

    return matches
