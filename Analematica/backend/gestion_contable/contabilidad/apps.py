from django.apps import AppConfig

class AdminContabilidadConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.admin_plataforma.gestion_contable.contabilidad'
    label = 'admin_contabilidad'
    verbose_name = 'Admin Accounting (Proxy)'

    def ready(self):
        import apps.admin_plataforma.gestion_contable.contabilidad.signals
