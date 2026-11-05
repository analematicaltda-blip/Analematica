# domain/services/asset_service.py
from infrastructure.models import Asset, Tenant

def create_asset(tenant: Tenant, asset_type: str, content: str) -> Asset:
    """
    Crea un nuevo asset para un tenant específico.
    """
    asset = Asset.objects.create(
        tenant=tenant,
        asset_type=asset_type,
        content=content
    )
    return asset
