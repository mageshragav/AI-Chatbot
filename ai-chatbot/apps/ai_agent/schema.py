"""
Pydantic schemas for API request/response validation.
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID


# ============================================================================
# Query Generation Schemas
# ============================================================================

class QueryRequest(BaseModel):
    """Request schema for generating ORM queries"""
    query: str = Field(..., min_length=1, max_length=1000, description="Natural language query")
    project_id: Optional[str] = Field(None, description="Project ID (optional if using API key)")
    include_explanation: bool = Field(True, description="Include explanation in response")
    include_metadata: bool = Field(True, description="Include models_used and filters_applied")
    
    @validator('query')
    def query_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty or whitespace only')
        return v.strip()


class QueryResponse(BaseModel):
    """Response schema for generated ORM queries"""
    query_id: str = Field(..., description="Unique query ID for tracking")
    django_orm_code: str = Field(..., description="Generated Django ORM query")
    explanation: Optional[str] = Field(None, description="Human-readable explanation")
    models_used: Optional[List[str]] = Field(None, description="List of Django models used")
    filters_applied: Optional[List[str]] = Field(None, description="List of filters applied")
    execution_time_ms: int = Field(..., description="Total execution time in milliseconds")
    success: bool = Field(True, description="Whether query generation succeeded")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query_id": "123e4567-e89b-12d3-a456-426614174000",
                "django_orm_code": "Product.objects.filter(is_active=True)",
                "explanation": "Filtered products by is_active field",
                "models_used": ["Product"],
                "filters_applied": ["is_active=True"],
                "execution_time_ms": 1250,
                "success": True
            }
        }


class BatchQueryRequest(BaseModel):
    """Request schema for batch query generation"""
    queries: List[str] = Field(..., min_items=1, max_items=50, description="List of queries (max 50)")
    project_id: Optional[str] = None
    include_explanation: bool = True
    include_metadata: bool = True


class BatchQueryResponse(BaseModel):
    """Response schema for batch queries"""
    results: List[QueryResponse]
    total_queries: int
    successful_queries: int
    failed_queries: int
    total_execution_time_ms: int


# ============================================================================
# Project Management Schemas
# ============================================================================

class ProjectCreate(BaseModel):
    """Schema for creating a new project"""
    name: str = Field(..., min_length=1, max_length=255, description="Project name (unique)")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    
    @validator('name')
    def name_valid(cls, v):
        # Only allow alphanumeric, hyphens, underscores
        if not v.replace('-', '').replace('_', '').replace(' ', '').isalnum():
            raise ValueError('Name can only contain letters, numbers, hyphens, underscores, and spaces')
        return v.strip()


class ProjectResponse(BaseModel):
    """Schema for project information"""
    id: str
    name: str
    description: Optional[str]
    api_key: str
    schema_version: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectUpdate(BaseModel):
    """Schema for updating project"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    is_active: Optional[bool] = None


class APIKeyResponse(BaseModel):
    """Response when regenerating API key"""
    project_id: str
    api_key: str
    message: str = "API key regenerated successfully. Store it securely - it won't be shown again."


# ============================================================================
# Schema Management Schemas
# ============================================================================

class ModelFieldInfo(BaseModel):
    """Information about a Django model field"""
    name: str
    field_type: str  # CharField, IntegerField, etc.
    max_length: Optional[int] = None
    null: bool = False
    blank: bool = False
    unique: bool = False
    choices: Optional[List[tuple]] = None
    help_text: Optional[str] = None


class ModelRelationship(BaseModel):
    """Information about model relationships"""
    field_name: str
    relation_type: str  # ForeignKey, ManyToMany, OneToOne
    related_model: str
    on_delete: Optional[str] = None


class ModelSchema(BaseModel):
    """Schema for a Django model"""
    model_name: str
    app_label: Optional[str] = None
    table_name: Optional[str] = None
    fields: List[ModelFieldInfo]
    relationships: List[ModelRelationship] = []


class SchemaUploadRequest(BaseModel):
    """Request schema for uploading Django model schemas"""
    project_name: str = Field(..., description="Project name")
    models: List[ModelSchema] = Field(..., min_items=1, description="List of Django models")
    auto_vectorize: bool = Field(True, description="Automatically create vector embeddings")


class SchemaUploadResponse(BaseModel):
    """Response after schema upload"""
    project_id: str
    models_uploaded: int
    vectorization_status: str  # "completed", "pending", "failed"
    message: str


class ExampleQueryCreate(BaseModel):
    """Schema for creating example queries"""
    user_query: str = Field(..., min_length=1, max_length=1000)
    orm_query: str = Field(..., min_length=1, max_length=2000)
    category: Optional[str] = Field(None, max_length=255)
    models_involved: List[str] = []


class ExamplesUploadRequest(BaseModel):
    """Request schema for uploading few-shot examples"""
    project_name: str
    examples: List[ExampleQueryCreate] = Field(..., min_items=1)
    auto_vectorize: bool = True


class ExamplesUploadResponse(BaseModel):
    """Response after examples upload"""
    project_id: str
    examples_uploaded: int
    vectorization_status: str
    message: str


# ============================================================================
# Query History Schemas
# ============================================================================

class QueryHistoryResponse(BaseModel):
    """Schema for query history item"""
    id: str
    project_id: str
    user_query: str
    orm_query: str
    explanation: Optional[str]
    models_used: List[str]
    filters_applied: List[str]
    execution_time_ms: int
    success: bool
    error_message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class QueryHistoryListResponse(BaseModel):
    """Schema for paginated query history"""
    items: List[QueryHistoryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class QueryHistoryFilter(BaseModel):
    """Filters for query history"""
    project_id: Optional[str] = None
    success: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search: Optional[str] = None  # Search in user_query


# ============================================================================
# Error Schemas
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ValidationErrorResponse(BaseModel):
    """Validation error response"""
    error: str = "Validation Error"
    details: List[Dict[str, Any]]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# Health Check Schemas
# ============================================================================

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    version: str
    database: str = "connected"
    vector_store: str = "connected"
    llm: str = "connected"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
