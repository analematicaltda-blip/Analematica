import uuid
from django.db import models

class SaaSLead(models.Model):
    class Status(models.TextChoices):
        NEW = 'NEW', 'New'
        CONTACTED = 'CONTACTED', 'Contacted'
        QUALIFIED = 'QUALIFIED', 'Qualified'
        PROPOSAL_SENT = 'PROPOSAL_SENT', 'Proposal Sent'
        NEGOTIATION = 'NEGOTIATION', 'Negotiation'
        CONVERTED = 'CONVERTED', 'Converted'
        LOST = 'LOST', 'Lost'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_name = models.CharField(max_length=255)
    contact_email = models.EmailField(unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    score = models.IntegerField(default=0)

    # Industry and Size for Scoring
    industry = models.CharField(max_length=100, blank=True, null=True)
    estimated_size = models.IntegerField(default=1, help_text="Number of employees or estimated scale.")

    # Tracking
    source = models.CharField(max_length=100, default='web')
    utm_source = models.CharField(max_length=100, blank=True, null=True)
    utm_campaign = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company_name} ({self.status})"

    class Meta:
        verbose_name = "Lead SaaS"
        verbose_name_plural = "Leads SaaS"
