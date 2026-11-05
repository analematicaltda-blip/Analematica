from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        # Importar las señales para que se registren correctamente en la aplicación
        import sys
        if 'makemigrations' not in sys.argv:
            import api.signals