from django.apps import AppConfig

class FacturacionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.prestadores.mi_negocio.facturacion'

    def ready(self):
        # Importar las señales para que los receptores se conecten.
        import apps.prestadores.mi_negocio.facturacion.signals
