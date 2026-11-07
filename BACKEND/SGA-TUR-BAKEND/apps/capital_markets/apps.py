from django.apps import AppConfig

class CapitalMarketsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.capital_markets'
    verbose_name = 'Capital Markets Integration Layer (Sarita Group)'

    def ready(self):
        # Registration of market-level listeners
        from .application.market_orchestrator import MarketOrchestrator
        MarketOrchestrator.register_handlers()
