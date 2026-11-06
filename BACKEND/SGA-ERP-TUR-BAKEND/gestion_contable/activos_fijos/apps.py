from django.apps import AppConfig

class ActivosFijosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.prestadores.mi_negocio.gestion_contable.activos_fijos'

    def ready(self):
        import apps.prestadores.mi_negocio.gestion_contable.activos_fijos.signals
