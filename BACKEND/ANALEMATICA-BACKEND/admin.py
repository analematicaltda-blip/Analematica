from django.contrib import admin
from .models import GovernancePolicy, GovernancePolicyVersion

class GovernancePolicyVersionInline(admin.TabularInline):
    model = GovernancePolicyVersion
    extra = 0
    readonly_fields = ('version_number', 'config_snapshot', 'reason_for_change', 'changed_by', 'created_at')

@admin.register(GovernancePolicy)
class GovernancePolicyAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'domain', 'is_active', 'created_at')
    list_filter = ('type', 'domain', 'is_active')
    search_fields = ('name', 'description')
    inlines = [GovernancePolicyVersionInline]

    def save_model(self, request, obj, form, change):
        if change:
            # Automatic Versioning on change
            last_version = obj.versions.order_by('-version_number').first()
            next_version_num = (last_version.version_number + 1) if last_version else 1

            GovernancePolicyVersion.objects.create(
                policy=obj,
                version_number=next_version_num,
                config_snapshot=obj.config,
                reason_for_change="Actualización vía Panel Administrativo",
                changed_by=request.user
            )
        super().save_model(request, obj, form, change)
