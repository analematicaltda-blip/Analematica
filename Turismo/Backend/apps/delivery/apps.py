from django.apps import AppConfig

class DeliveryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.delivery'
    verbose_name = 'Plataforma de Delivery Institucional'

    def ready(self):
        from .handlers import DeliveryEventHandlers
        DeliveryEventHandlers.register_all()
