"""
API Routes for AI Agent
"""
from fastapi import APIRouter, HTTPException, Depends, Request, status
from typing import List, Optional
from uuid import UUID
import logging

from apps.ai_agent.models import ProjectConfig, QueryHistory
from apps.ai_agent.schema import (
    QueryRequest, QueryResponse,
    BatchQueryRequest, BatchQueryResponse,
    ProjectCreate, ProjectResponse, ProjectUpdate, APIKeyResponse,
    QueryHistoryResponse, QueryHistoryListResponse,
    ErrorResponse
)
from apps.ai_agent.services.query_service import query_service
from apps.ai_agent.middleware.auth import get_project_from_api_key

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai_agent", tags=["AI Agent"])


# ============================================================================
# Query Generation Endpoints
# ============================================================================

@router.post(
    "/query",
    response_model=QueryResponse,
    summary="Generate Django ORM Query",
    description="Convert natural language query to Django ORM code",
    responses={
        401: {"model": ErrorResponse, "description": "Invalid API key"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def generate_query(
    request_body: QueryRequest,
    request: Request,
    project: ProjectConfig = Depends(get_project_from_api_key)
):
    """
    Generate Django ORM query from natural language.
    
    **Authentication:** Requires `X-API-Key` header
    
    **Example Request:**
    ```json
    {
        "query": "List all active users",
        "include_explanation": true,
        "include_metadata": true
    }
    ```
    
    **Example Response:**
    ```json
    {
        "query_id": "123e4567-e89b-12d3-a456-426614174000",
        "django_orm_code": "User.objects.filter(is_active=True)",
        "explanation": "Filtered users by is_active field",
        "models_used": ["User"],
        "filters_applied": ["is_active=True"],
        "execution_time_ms": 1250,
        "success": true
    }
    ```
    """
    try:
        # Get client info
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Generate query
        response = await query_service.generate_orm_query(
            request=request_body,
            project=project,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return response
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating query: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate query. Please try again."
        )


@router.post(
    "/query/batch",
    response_model=BatchQueryResponse,
    summary="Generate Multiple ORM Queries",
    description="Convert multiple natural language queries to Django ORM code in a single request"
)
async def generate_batch_queries(
    request_body: BatchQueryRequest,
    request: Request,
    project: ProjectConfig = Depends(get_project_from_api_key)
):
    """
    Generate multiple Django ORM queries in batch.
    
    **Limit:** Maximum 50 queries per request
    """
    results = []
    successful = 0
    failed = 0
    total_time = 0
    
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    for query_text in request_body.queries:
        try:
            query_request = QueryRequest(
                query=query_text,
                include_explanation=request_body.include_explanation,
                include_metadata=request_body.include_metadata
            )
            
            response = await query_service.generate_orm_query(
                request=query_request,
                project=project,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            results.append(response)
            successful += 1
            total_time += response.execution_time_ms
            
        except Exception as e:
            logger.error(f"Error in batch query: {str(e)}")
            failed += 1
            # Add error response
            results.append(QueryResponse(
                query_id="",
                django_orm_code="",
                execution_time_ms=0,
                success=False
            ))
    
    return BatchQueryResponse(
        results=results,
        total_queries=len(request_body.queries),
        successful_queries=successful,
        failed_queries=failed,
        total_execution_time_ms=total_time
    )


# ============================================================================
# Query History Endpoints
# ============================================================================

@router.get(
    "/history",
    response_model=QueryHistoryListResponse,
    summary="Get Query History",
    description="Retrieve query history for the authenticated project"
)
async def get_query_history(
    page: int = 1,
    page_size: int = 50,
    success_only: Optional[bool] = None,
    project: ProjectConfig = Depends(get_project_from_api_key)
):
    """
    Get paginated query history.
    
    **Parameters:**
    - `page`: Page number (default: 1)
    - `page_size`: Items per page (default: 50, max: 100)
    - `success_only`: Filter by success status (optional)
    """
    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be >= 1")
    if page_size < 1 or page_size > 100:
        raise HTTPException(status_code=400, detail="Page size must be between 1 and 100")
    
    offset = (page - 1) * page_size
    
    queries, total = await query_service.get_query_history(
        project=project,
        limit=page_size,
        offset=offset,
        success_only=success_only
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return QueryHistoryListResponse(
        items=[QueryHistoryResponse.from_orm(q) for q in queries],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get(
    "/history/{query_id}",
    response_model=QueryHistoryResponse,
    summary="Get Query Details",
    description="Get details of a specific query by ID"
)
async def get_query_details(
    query_id: UUID,
    project: ProjectConfig = Depends(get_project_from_api_key)
):
    """Get specific query details"""
    query = await query_service.get_query_by_id(query_id)
    
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    
    # Verify query belongs to this project
    if query.project_id != project.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return QueryHistoryResponse.from_orm(query)


@router.get(
    "/stats",
    summary="Get Project Statistics",
    description="Get query statistics for the authenticated project"
)
async def get_project_stats(
    project: ProjectConfig = Depends(get_project_from_api_key)
):
    """Get project statistics"""
    stats = await query_service.get_project_stats(project)
    return stats


# ============================================================================
# Project Management Endpoints (Admin)
# ============================================================================

@router.post(
    "/projects",
    response_model=ProjectResponse,
    summary="Create New Project",
    description="Create a new project configuration (generates API key)",
    status_code=status.HTTP_201_CREATED
)
async def create_project(project_data: ProjectCreate):
    """
    Create a new project.
    
    **Note:** This endpoint is not protected by API key authentication.
    In production, you should add admin authentication.
    """
    # Check if project name already exists
    existing = await ProjectConfig.get_or_none(name=project_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Project with name '{project_data.name}' already exists"
        )
    
    # Generate API key
    api_key = await ProjectConfig.generate_api_key()
    
    # Create project
    project = await ProjectConfig.create(
        name=project_data.name,
        description=project_data.description,
        api_key=api_key
    )
    
    logger.info(f"Created new project: {project.name}")
    
    return ProjectResponse.from_orm(project)


@router.get(
    "/projects",
    response_model=List[ProjectResponse],
    summary="List All Projects",
    description="List all projects (admin endpoint)"
)
async def list_projects(
    is_active: Optional[bool] = None,
    limit: int = 100
):
    """
    List all projects.
    
    **Note:** In production, add admin authentication.
    """
    query = ProjectConfig.all()
    
    if is_active is not None:
        query = query.filter(is_active=is_active)
    
    projects = await query.limit(limit).order_by('-created_at')
    
    return [ProjectResponse.from_orm(p) for p in projects]


@router.get(
    "/projects/{project_id}",
    response_model=ProjectResponse,
    summary="Get Project Details",
    description="Get details of a specific project"
)
async def get_project(project_id: UUID):
    """Get project details by ID"""
    project = await ProjectConfig.get_or_none(id=project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return ProjectResponse.from_orm(project)


@router.post(
    "/projects/{project_id}/regenerate-key",
    response_model=APIKeyResponse,
    summary="Regenerate API Key",
    description="Generate a new API key for a project (invalidates old key)"
)
async def regenerate_api_key(project_id: UUID):
    """
    Regenerate API key for a project.
    
    **Warning:** This will invalidate the old API key!
    """
    project = await ProjectConfig.get_or_none(id=project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Generate new API key
    new_api_key = await ProjectConfig.generate_api_key()
    project.api_key = new_api_key
    await project.save()
    
    logger.warning(f"Regenerated API key for project: {project.name}")
    
    return APIKeyResponse(
        project_id=str(project.id),
        api_key=new_api_key
    )


@router.delete(
    "/projects/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Project",
    description="Delete a project and all associated data"
)
async def delete_project(project_id: UUID):
    """
    Delete a project.
    
    **Warning:** This will delete all query history and schemas!
    """
    project = await ProjectConfig.get_or_none(id=project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    await project.delete()
    logger.warning(f"Deleted project: {project.name}")
    
    return None