from django.apps import AppConfig

class GestionComercialConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.prestadores.mi_negocio.gestion_comercial'

    def ready(self):
        from .pool08 import identity_models, crm_models, opportunity_models, pricing_models, quotation_models, sales_models, payment_models, landing_models, capture_models, library_models, generation_models, email_campaign_models, mobile_message_models, analytics_models,army_models,ads_models,inbox_models,publishing_models

        import apps.prestadores.mi_negocio.gestion_comercial.signals

        # Register the existing funnel models during app discovery, not URL import order.
        from .funnels import models as funnel_models
        from .marketing import models as marketing_models
        from .shared import models as shared_models
