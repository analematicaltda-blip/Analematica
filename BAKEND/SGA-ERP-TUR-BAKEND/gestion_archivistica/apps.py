from django.apps import AppConfig
import os

class GestionArchivisticaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.prestadores.mi_negocio.gestion_archivistica'
    verbose_name = 'Gestión Archivística'
    path = os.path.join(os.path.dirname(__file__))
