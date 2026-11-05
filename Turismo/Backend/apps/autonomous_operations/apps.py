from django.apps import AppConfig

class AutonomousOperationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.autonomous_operations'
    verbose_name = 'Autonomous Operations'

    def ready(self):
        from .agent_registry import AgentRegistry
        from .policy_engine import PolicyEngine
        try:
            AgentRegistry.register_default_agents()
            PolicyEngine.initialize_default_policies()
        except:
            pass # Avoid failure during initial migrations
