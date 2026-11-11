"""Persist real CRM state atomically; no invoice, payment or ledger side effects."""
from decimal import Decimal
from django.db import transaction
from ..models import Opportunity,Lead
from apps.core_erp.accounting.validation import money,exact_arithmetic


def crm_amount(value):
    amount=money(value)
    if amount>Decimal('9999999999.99'):raise ValueError('CRM amount exceeds field precision.')
    return amount

class FunnelEngine:
    @staticmethod
    @exact_arithmetic
    @transaction.atomic
    def create_opportunity(lead,expected_plan,estimated_revenue):
        if not isinstance(expected_plan,str) or not 1<=len(expected_plan)<=100:raise ValueError('Explicit target plan required.')
        amount=crm_amount(estimated_revenue)
        stored=Lead.objects.select_for_update().get(pk=lead.pk)
        if stored.status==Lead.Status.REJECTED:raise ValueError('Rejected lead cannot create an opportunity.')
        return Opportunity.objects.create(lead=stored,expected_plan=expected_plan,estimated_revenue=amount,stage=Opportunity.Stage.PROSPECTING,probability=10)

    @staticmethod
    @transaction.atomic
    def transition_stage(opportunity,new_stage):
        if not isinstance(new_stage,str) or new_stage not in Opportunity.Stage.values:raise ValueError('Unsupported CRM stage.')
        hint=Opportunity.objects.get(pk=opportunity.pk)
        lead=Lead.objects.select_for_update().get(pk=hint.lead_id)
        stored=Opportunity.objects.select_for_update().get(pk=opportunity.pk)
        if stored.lead_id!=lead.pk:raise ValueError('CRM customer changed; reload before transition.')
        if stored.stage not in Opportunity.Stage.values:raise ValueError('Legacy stage requires explicit reconciliation.')
        if stored.stage in {Opportunity.Stage.WON,Opportunity.Stage.LOST} and new_stage!=stored.stage:raise ValueError('Closed opportunity requires an explicit recovery process.')
        if lead.status==Lead.Status.REJECTED and new_stage!=Opportunity.Stage.LOST:raise ValueError('Rejected lead cannot progress.')
        probabilities={Opportunity.Stage.PROSPECTING:10,Opportunity.Stage.PROPOSAL:30,Opportunity.Stage.NEGOTIATION:60,Opportunity.Stage.WON:100,Opportunity.Stage.LOST:0}
        stored.stage=new_stage;stored.probability=probabilities[new_stage];stored.save(update_fields=['stage','probability'])
        if new_stage==Opportunity.Stage.WON:
            lead.status=Lead.Status.CONVERTED;lead.save(update_fields=['status','updated_at'])
        return stored
