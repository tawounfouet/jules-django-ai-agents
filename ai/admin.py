from django.contrib import admin
from .models import AgentConfig

@admin.register(AgentConfig)
class AgentConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'model_name', 'temperature', 'is_active', 'updated_at')
    list_filter = ('provider', 'is_active')
    search_fields = ('name', 'model_name')
