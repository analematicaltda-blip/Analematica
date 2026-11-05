# domain/services/sales_service.py
from sales.models import Opportunity
from sales.serializers import OpportunitySerializer

def get_all_opportunities(user):
    """
    Retrieves all opportunities for a given user.
    """
    opportunities = Opportunity.objects.filter(tenant=user.tenant)
    serializer = OpportunitySerializer(opportunities, many=True)
    return serializer.data
