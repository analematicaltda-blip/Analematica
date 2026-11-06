from django.apps import AppConfig

class GestionComercialConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.prestadores.mi_negocio.gestion_comercial'

    def ready(self):
        import apps.prestadores.mi_negocio.gestion_comercial.signals
