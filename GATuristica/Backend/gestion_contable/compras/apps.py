from django.apps import AppConfig

class ComprasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.prestadores.mi_negocio.gestion_contable.compras'

    def ready(self):
        import apps.prestadores.mi_negocio.gestion_contable.compras.signals
