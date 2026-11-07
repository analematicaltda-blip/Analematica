from django.contrib import admin
from .models import Project, ProjectIncome, ProjectCost

class ProjectIncomeInline(admin.TabularInline):
    model = ProjectIncome
    extra = 1

class ProjectCostInline(admin.TabularInline):
    model = ProjectCost
    extra = 1

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'status', 'budget_allocated')
    search_fields = ('name',)
    list_filter = ('status',)
    inlines = [ProjectIncomeInline, ProjectCostInline]

@admin.register(ProjectIncome)
class ProjectIncomeAdmin(admin.ModelAdmin):
    list_display = ('project', 'description', 'amount', 'date')
    search_fields = ('project__name', 'description')

@admin.register(ProjectCost)
class ProjectCostAdmin(admin.ModelAdmin):
    list_display = ('project', 'description', 'amount', 'date')
    search_fields = ('project__name', 'description')
