"""
Database models for AI Agent application.
Stores project configurations, query history, and metadata.
"""
from tortoise.models import Model
from tortoise import fields
import uuid
import secrets


class ProjectConfig(Model):
    """
    Store Django project configurations for multi-tenant support.
    Each project gets its own API key and isolated vector stores.
    """
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    name = fields.CharField(max_length=255, unique=True, index=True)
    description = fields.TextField(null=True)
    api_key = fields.CharField(max_length=255, unique=True, index=True)
    schema_version = fields.CharField(max_length=50, default="1.0")
    is_active = fields.BooleanField(default=True, index=True)
    
    # Metadata
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "project_configs"
        ordering = ["-created_at"]
    
    @classmethod
    async def generate_api_key(cls) -> str:
        """Generate a secure API key with prefix"""
        return f"sk_proj_{secrets.token_urlsafe(32)}"
    
    def __str__(self):
        return f"Project: {self.name}"


class QueryHistory(Model):
    """
    Store all query requests and responses for audit trail and analytics.
    """
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    project = fields.ForeignKeyField(
        'models.ProjectConfig', 
        related_name='queries',
        on_delete=fields.CASCADE
    )
    
    # Query data
    user_query = fields.TextField()
    orm_query = fields.TextField()
    explanation = fields.TextField(null=True)
    models_used = fields.JSONField(default=list)  # List of model names
    filters_applied = fields.JSONField(default=list)  # List of filters
    
    # Performance metrics
    execution_time_ms = fields.IntField(default=0)
    vector_search_time_ms = fields.IntField(default=0)
    llm_time_ms = fields.IntField(default=0)
    
    # Status
    success = fields.BooleanField(default=True)
    error_message = fields.TextField(null=True)
    
    # Metadata
    created_at = fields.DatetimeField(auto_now_add=True, index=True)
    ip_address = fields.CharField(max_length=45, null=True)  # IPv6 support
    user_agent = fields.TextField(null=True)
    
    class Meta:
        table = "query_history"
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"Query: {self.user_query[:50]}..."


class SchemaMetadata(Model):
    """
    Store metadata about uploaded Django model schemas.
    """
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    project = fields.ForeignKeyField(
        'models.ProjectConfig',
        related_name='schemas',
        on_delete=fields.CASCADE
    )
    
    # Schema information
    model_name = fields.CharField(max_length=255, index=True)
    app_label = fields.CharField(max_length=255, null=True)
    table_name = fields.CharField(max_length=255, null=True)
    fields_info = fields.JSONField(default=dict)  # Field definitions
    relationships = fields.JSONField(default=dict)  # FK, M2M info
    
    # Vector store info
    vector_collection_name = fields.CharField(max_length=255)
    is_vectorized = fields.BooleanField(default=False)
    
    # Metadata
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "schema_metadata"
        unique_together = (("project", "model_name"),)
    
    def __str__(self):
        return f"{self.project.name}: {self.model_name}"


class ExampleQuery(Model):
    """
    Store few-shot example queries for better ORM generation.
    """
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    project = fields.ForeignKeyField(
        'models.ProjectConfig',
        related_name='examples',
        on_delete=fields.CASCADE
    )
    
    # Example data
    user_query = fields.TextField()
    orm_query = fields.TextField()
    category = fields.CharField(max_length=255, null=True, index=True)  # e.g., "filtering", "aggregation"
    models_involved = fields.JSONField(default=list)
    
    # Vector store info
    is_vectorized = fields.BooleanField(default=False)
    
    # Metadata
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "example_queries"
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"Example: {self.user_query[:50]}..."
