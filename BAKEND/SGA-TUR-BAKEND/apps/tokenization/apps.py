from django.apps import AppConfig

class TokenizationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tokenization'
    verbose_name = 'Programmable Capital Infrastructure (Tokenization)'

    def ready(self):
        # Registration of tokenization event handlers
        from .application.token_orchestrator import TokenOrchestrator
        TokenOrchestrator.register_handlers()
