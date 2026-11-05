# SaritaUnificado/backend/api/signals.py

# TODO: Lógica de Puntuación Desactivada Temporalmente
# El siguiente código de señales ha sido comentado porque depende del modelo obsoleto 'Perfil'
# y de campos de puntuación ('puntuacion_capacitacion', 'puntuacion_reseñas') que ya no existen
# en el modelo refactorizado 'ProviderProfile'.
# Es necesario re-evaluar e implementar una nueva lógica de scoring acorde a la nueva arquitectura.

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import AsistenciaCapacitacion, Resena, ScoringRule, Verificacion
from apps.turismo.models.provider_models import TourismProvider
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=AsistenciaCapacitacion)
def update_score_on_capacitacion(sender, instance, created, **kwargs):
    if created:
        try:
            # Vía 2: Prestadores vinculados
            perfil = TourismProvider.objects.get(owner=instance.usuario)
            puntos = instance.capacitacion.puntos_asistencia
            perfil.puntuacion_capacitacion += puntos
            perfil.save(update_fields=['puntuacion_capacitacion'])
            perfil.recalcular_puntuacion_total()
            logger.info(f"Puntaje de capacitación actualizado para {perfil.name}: +{puntos}")
        except TourismProvider.DoesNotExist:
            # Artesanos (en api.models)
            if hasattr(instance.usuario, 'perfil_artesano'):
                art = instance.usuario.perfil_artesano
                art.puntuacion_capacitacion += instance.capacitacion.puntos_asistencia
                art.recalcular_puntuacion_total()


def register_security_monitors():
    from django.contrib.auth.signals import user_login_failed
    from apps.core_erp.event_bus import EventBus

    @receiver(user_login_failed)
    def track_failed_login(sender, credentials, request, **kwargs):
        """
        Omnisciencia: Monitoreo de intentos de login fallidos (Fase 4.4.2).
        """
        EventBus.emit(
            "IntentoFallidoLogin",
            {
                "username": credentials.get('username'),
                "ip": request.META.get('REMOTE_ADDR') if request else "unknown",
                "user_agent": request.META.get('HTTP_USER_AGENT') if request else "unknown"
            },
            severity="warning"
        )

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Artesano, CustomUser
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import ProviderProfile

@receiver(post_save, sender=Artesano)
def activar_perfil_comercial_artesano(sender, instance, **kwargs):
    """
    FASE 16: Activación automática del perfil productivo turístico
    tras la aprobación gubernamental del artesano.
    """
    if instance.aprobado:
        perfil, created = ProviderProfile.objects.get_or_create(
            usuario=instance.usuario,
            defaults={
                'nombre_comercial': instance.nombre_taller,
                'provider_type': ProviderProfile.ProviderTypes.ARTISAN,
                'is_active': True,
                'is_verified': True
            }
        )
        if not created and not perfil.is_active:
            perfil.is_active = True
            perfil.is_verified = True
            perfil.save(update_fields=['is_active', 'is_verified'])


@receiver(post_save, sender=Resena)
def update_score_on_resena(sender, instance, **kwargs):
    if instance.aprobada:
        target_model = instance.content_type.model_class()

        if target_model == TourismProvider:
            try:
                perfil = TourismProvider.objects.get(pk=instance.object_id)
                rules = ScoringRule.load()

                reseñas_aprobadas = Resena.objects.filter(
                    content_type=instance.content_type,
                    object_id=instance.object_id,
                    aprobada=True
                )
                perfil.puntuacion_resenas = sum(
                    r.calificacion * rules.puntos_por_estrella_reseña for r in reseñas_aprobadas
                )
                perfil.save(update_fields=['puntuacion_resenas'])
                perfil.recalcular_puntuacion_total()
            except TourismProvider.DoesNotExist:
                pass
        elif target_model == Artesano:
             instance.content_object.recalcular_puntuacion_total()

@receiver(post_save, sender=Verificacion)
def update_score_on_verificacion(sender, instance, **kwargs):
    """
    Actualiza el puntaje del prestador basado en la visita de cumplimiento.
    """
    try:
        # Buscamos el prestador via la referencia UUID del modelo Turismo
        perfil = TourismProvider.objects.get(id=instance.prestador_ref_id)
        perfil.puntuacion_verificacion = instance.puntaje_obtenido
        perfil.save(update_fields=['puntuacion_verificacion'])
        perfil.recalcular_puntuacion_total()
        logger.info(f"Puntaje de verificación actualizado para {perfil.name}: {perfil.puntuacion_verificacion}")
    except TourismProvider.DoesNotExist:
        pass
