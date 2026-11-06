from django.apps import AppConfig


class AutomationConfig(AppConfig):
 
    default_auto_field = "django.db.models.BigAutoField"
    name = "automation"

    def ready(self):
        # Importar y registrar los suscriptores cuando la app esté lista
        from . import subscribers
        subscribers.register_subscribers()
 
