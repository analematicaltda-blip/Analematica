# domain/services/campaign_service.py
from infrastructure.models import Campaign, Tenant
from typing import List

def create_campaign(tenant: Tenant, name: str, goal: str = '') -> Campaign:
    """
    Crea una nueva campaña para un tenant específico.
    """
    campaign = Campaign.objects.create(
        tenant=tenant,
        name=name,
        goal=goal
    )
    return campaign

def get_campaign_by_id(tenant: Tenant, campaign_id: int) -> Campaign:
    """
    Obtiene una campaña por su ID, asegurando que pertenezca al tenant correcto.
    """
    try:
        return Campaign.objects.get(id=campaign_id, tenant=tenant)
    except Campaign.DoesNotExist:
        raise ValueError("Campaign not found in this tenant.")

def list_campaigns_for_tenant(tenant: Tenant) -> List[Campaign]:
    """
    Lista todas las campañas de un tenant.
    """
    return Campaign.objects.filter(tenant=tenant)

def update_campaign(tenant: Tenant, campaign_id: int, name: str, goal: str) -> Campaign:
    """
    Actualiza una campaña existente.
    """
    campaign = get_campaign_by_id(tenant, campaign_id)
    campaign.name = name
    campaign.goal = goal
    campaign.save()
    return campaign

def delete_campaign(tenant: Tenant, campaign_id: int):
    """
    Elimina una campaña.
    """
    campaign = get_campaign_by_id(tenant, campaign_id)
    campaign.delete()
