from django.apps import AppConfig

class GestionComercialConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.prestadores.mi_negocio.gestion_comercial'

    def ready(self):
        import apps.prestadores.mi_negocio.gestion_comercial.signals

        # Register the existing funnel models during app discovery, not URL import order.
        from .funnels import models as funnel_models
