# domain/services/customer_service.py
from infrastructure.models import Customer, Tenant
from typing import List

def create_customer(tenant: Tenant, email: str, first_name: str = '', last_name: str = '') -> Customer:
    """
    Crea un nuevo cliente para un tenant específico.
    """
    customer = Customer.objects.create(
        tenant=tenant,
        email=email,
        first_name=first_name,
        last_name=last_name
    )
    return customer

def get_customer_by_id(tenant: Tenant, customer_id: int) -> Customer:
    """
    Obtiene un cliente por su ID, asegurando que pertenezca al tenant correcto.
    """
    try:
        return Customer.objects.get(id=customer_id, tenant=tenant)
    except Customer.DoesNotExist:
        raise ValueError("Customer not found in this tenant.")

def list_customers_for_tenant(tenant: Tenant) -> List[Customer]:
    """
    Lista todos los clientes de un tenant.
    """
    return Customer.objects.filter(tenant=tenant)
