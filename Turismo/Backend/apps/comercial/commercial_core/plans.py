import logging
from ..models import Plan, PlanTier, AddOn

logger = logging.getLogger(__name__)

class PlanManager:
    """
    Gestiona la lógica de negocio de los planes y sus versiones.
    """

    @staticmethod
    def create_plan_version(base_code, name, monthly_price, yearly_price, **kwargs):
        """
        Crea una nueva versión de un plan existente o uno nuevo.
        """
        last_version = Plan.objects.filter(code=base_code).order_by('-version').first()
        new_version = (last_version.version + 1) if last_version else 1

        plan = Plan.objects.create(
            code=base_code,
            name=name,
            version=new_version,
            monthly_price=monthly_price,
            yearly_price=yearly_price,
            **kwargs
        )

        if last_version:
            last_version.is_active = False
            last_version.save()

        return plan

    @staticmethod
    def add_tier_to_plan(plan, from_unit, to_unit, price_per_unit):
        return PlanTier.objects.create(
            plan=plan,
            from_unit=from_unit,
            to_unit=to_unit,
            price_per_unit=price_per_unit
        )
