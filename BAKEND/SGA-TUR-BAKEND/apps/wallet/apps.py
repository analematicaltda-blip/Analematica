from django.apps import AppConfig
from django.db.models.signals import post_save

class WalletConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.wallet'
    verbose_name = 'Monedero Institucional'

    def ready(self):
        import apps.wallet.signals
        from .handlers import WalletEventHandlers
        WalletEventHandlers.register_all()
