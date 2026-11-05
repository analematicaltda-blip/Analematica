from django.apps import AppConfig

class FacturacionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.admin_plataforma.facturacion'

    def ready(self):
        # Importar las señales para que los receptores se conecten.
        import apps.admin_plataforma.facturacion.signals
