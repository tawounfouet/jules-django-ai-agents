from django.contrib import admin
from .models import (
    Agent, Tool, AgentTool,
    Graph, GraphVersion,
    Execution, ExecutionStep,
    AgentMessage, AgentMemory, KnowledgeSource
)

class AgentToolInline(admin.TabularInline):
    model = AgentTool
    extra = 1

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'llm_provider', 'llm_model', 'is_active')
    list_filter = ('llm_provider', 'is_active')
    search_fields = ('name', 'key')
    inlines = [AgentToolInline]

@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'python_path', 'is_sensitive')
    search_fields = ('name', 'key', 'python_path')

@admin.register(Graph)
class GraphAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'is_active', 'entry_agent')
    search_fields = ('name', 'key')

@admin.register(GraphVersion)
class GraphVersionAdmin(admin.ModelAdmin):
    list_display = ('graph', 'version', 'created_at')
    list_filter = ('graph',)

@admin.register(Execution)
class ExecutionAdmin(admin.ModelAdmin):
    list_display = ('id', 'graph', 'status', 'triggered_by', 'started_at')
    list_filter = ('status', 'triggered_by', 'graph')
    readonly_fields = ('started_at', 'finished_at')

@admin.register(ExecutionStep)
class ExecutionStepAdmin(admin.ModelAdmin):
    list_display = ('execution', 'agent', 'node_name', 'status', 'started_at')
    list_filter = ('status', 'agent')

@admin.register(AgentMessage)
class AgentMessageAdmin(admin.ModelAdmin):
    list_display = ('role', 'agent', 'execution', 'created_at')
    list_filter = ('role', 'agent')
    search_fields = ('content',)

@admin.register(KnowledgeSource)
class KnowledgeSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'type', 'is_active')
    list_filter = ('type', 'is_active')
