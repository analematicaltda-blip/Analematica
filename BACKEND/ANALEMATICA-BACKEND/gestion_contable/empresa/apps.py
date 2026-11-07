from django.apps import AppConfig

class AdminCompanyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.admin_plataforma.gestion_contable.empresa'
    label = 'admin_company'
    verbose_name = 'Admin Company Profile'
