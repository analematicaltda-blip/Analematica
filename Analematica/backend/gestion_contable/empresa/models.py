from django.db import models
from apps.core_erp.base_models import CompanyBase

class AdminCompany(CompanyBase):
    """
    Represents the main legal entity of the Holding (Sarita).
    """
    is_holding = models.BooleanField(default=True)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'admin_company'
        db_table = 'admin_company_profile'
        verbose_name = "Admin Company"
