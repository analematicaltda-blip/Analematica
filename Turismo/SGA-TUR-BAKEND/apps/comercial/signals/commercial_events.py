from django.dispatch import Signal

# Señales de Negocio SaaS
subscription_activated = Signal() # Provisto: [subscription]
subscription_renewed = Signal()   # Provisto: [subscription]
usage_limit_reached = Signal()    # Provisto: [subscription, metric_type]
payment_failed = Signal()        # Provisto: [subscription, reason]
plan_upgraded = Signal()         # Provisto: [subscription, old_plan, new_plan]
