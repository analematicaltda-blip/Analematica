from django.apps import AppConfig

class EnterpriseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.enterprise'
    verbose_name = 'Enterprise Operating System Core'

    def ready(self):
        # 1. Policy & Governance Handlers
        from .application.policy_service import PolicyEvaluationService
        PolicyEvaluationService.register_handlers()

        # 2. Decision Engine Handlers
        from .application.decision_engine_handler import register_decision_handlers
        register_decision_handlers()

        # 3. Intelligence & Forecast Handlers
        from .application.strategic_handler import register_strategic_handlers
        register_strategic_handlers()
