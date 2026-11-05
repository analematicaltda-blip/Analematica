from django.apps import AppConfig

class PresupuestoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.prestadores.mi_negocio.gestion_contable.presupuesto'

    def ready(self):
        import apps.prestadores.mi_negocio.gestion_contable.presupuesto.signals
