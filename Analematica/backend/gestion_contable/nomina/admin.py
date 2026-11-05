from django.contrib import admin
from .models import Employee, EmploymentContract, PayrollConcept, PayrollRun, PayrollNews, PayrollDetail

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'tax_id')

@admin.register(EmploymentContract)
class EmploymentContractAdmin(admin.ModelAdmin):
    list_display = ('employee', 'start_date', 'base_salary')

@admin.register(PayrollRun)
class PayrollRunAdmin(admin.ModelAdmin):
    list_display = ('year', 'month')

admin.site.register(PayrollConcept)
admin.site.register(PayrollNews)
admin.site.register(PayrollDetail)
