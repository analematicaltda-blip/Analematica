from django.apps import AppConfig

class InventarioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.prestadores.mi_negocio.gestion_contable.inventario'

    def ready(self):
        import apps.prestadores.mi_negocio.gestion_contable.inventario.signals
