from ..services.crm_service import CRMService
from ..services.subscription_service import SubscriptionService
from ..models import Plan

class ConversionPipeline:
    """
    Orquestador para convertir prospectos en clientes.
    """

    @staticmethod
    def execute_full_conversion(lead_id, plan_id, tenant_name):
        # 1. CRM Impact (Simulado)
        # 2. Subscription Impact
        plan = Plan.objects.get(id=plan_id)
        subscription = SubscriptionService.create_subscription(
            tenant_id=f"TENANT-{tenant_name[:5].upper()}",
            plan=plan
        )

        # 3. Activation
        SubscriptionService.activate_subscription(subscription.id)

        return {
            "status": "success",
            "subscription_id": subscription.id
        }
