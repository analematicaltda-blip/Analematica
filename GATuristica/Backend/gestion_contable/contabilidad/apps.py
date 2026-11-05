from django.apps import AppConfig

class ContabilidadConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.prestadores.mi_negocio.gestion_contable.contabilidad'
    label = 'tenant_contabilidad'
    verbose_name = 'Contabilidad (Proxy)'
