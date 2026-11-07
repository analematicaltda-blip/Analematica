from django.apps import AppConfig


class MiNegocioConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.prestadores.mi_negocio"

    def ready(self):
        # These models belong to parent app labels but live in nested packages.
        # Discover them before migration autodetection, not while importing URLs.
        from importlib import import_module
        for module in ['gestion_operativa.models',
                       'gestion_operativa.modulos_genericos.inventario.models',
                       'gestion_operativa.modulos_genericos.costos.models',
                       'gestion_operativa.modulos_genericos.horarios.models',
                       'gestion_operativa.modulos_genericos.valoraciones.models']:
            import_module(self.name+'.'+module)
