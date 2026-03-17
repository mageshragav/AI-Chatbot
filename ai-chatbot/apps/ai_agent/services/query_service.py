"""
Query Service - Handles ORM query generation and management
"""
import time
from typing import Optional, Dict, Any
from uuid import UUID
import logging

from apps.ai_agent.models import QueryHistory, ProjectConfig
from apps.ai_agent.schema import QueryRequest, QueryResponse
from apps.ai_agent.utils.query_validator import validator
from apps.ai_agent.agent_builder.agent import ORMQueryOutput

logger = logging.getLogger(__name__)


class QueryService:
    """Service for handling query generation and management"""
    
    def __init__(self):
        self.validator = validator
    
    async def generate_orm_query(
        self,
        request: QueryRequest,
        project: ProjectConfig,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> QueryResponse:
        """
        Generate ORM query from natural language.
        
        Args:
            request: Query request with user query
            project: Project configuration
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            QueryResponse with generated ORM query
        """
        start_time = time.time()
        
        try:
            # Import here to avoid circular imports
            from apps.ai_agent.agent_builder.agent import get_orm_response
            
            # Generate query using agent
            logger.info(f"Generating query for project {project.name}: {request.query}")
            agent_start = time.time()
            result: ORMQueryOutput = get_orm_response(request.query)
            agent_time = int((time.time() - agent_start) * 1000)
            
            # Validate generated query
            is_safe, sanitized_query, error = self.validator.validate_and_sanitize(
                result.django_orm_code
            )
            
            if not is_safe:
                logger.warning(f"Unsafe query generated: {error}")
                # Save failed query to history
                await self._save_query_history(
                    project=project,
                    user_query=request.query,
                    orm_query=result.django_orm_code,
                    success=False,
                    error_message=f"Query validation failed: {error}",
                    execution_time_ms=agent_time,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                raise ValueError(f"Generated query is unsafe: {error}")
            
            # Calculate execution time
            total_time = int((time.time() - start_time) * 1000)
            
            # Save to history
            history = await self._save_query_history(
                project=project,
                user_query=request.query,
                orm_query=sanitized_query,
                explanation=result.explanation if request.include_explanation else None,
                models_used=result.models_used if request.include_metadata else [],
                filters_applied=result.filters_applied if request.include_metadata else [],
                success=True,
                execution_time_ms=total_time,
                llm_time_ms=agent_time,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Build response
            response = QueryResponse(
                query_id=str(history.id),
                django_orm_code=sanitized_query,
                explanation=result.explanation if request.include_explanation else None,
                models_used=result.models_used if request.include_metadata else None,
                filters_applied=result.filters_applied if request.include_metadata else None,
                execution_time_ms=total_time,
                success=True
            )
            
            logger.info(f"Query generated successfully in {total_time}ms")
            return response
            
        except Exception as e:
            logger.error(f"Error generating query: {str(e)}", exc_info=True)
            
            # Save error to history
            total_time = int((time.time() - start_time) * 1000)
            await self._save_query_history(
                project=project,
                user_query=request.query,
                orm_query="",
                success=False,
                error_message=str(e),
                execution_time_ms=total_time,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            raise
    
    async def _save_query_history(
        self,
        project: ProjectConfig,
        user_query: str,
        orm_query: str,
        explanation: Optional[str] = None,
        models_used: Optional[list] = None,
        filters_applied: Optional[list] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        execution_time_ms: int = 0,
        vector_search_time_ms: int = 0,
        llm_time_ms: int = 0,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> QueryHistory:
        """Save query to history"""
        history = await QueryHistory.create(
            project=project,
            user_query=user_query,
            orm_query=orm_query,
            explanation=explanation,
            models_used=models_used or [],
            filters_applied=filters_applied or [],
            success=success,
            error_message=error_message,
            execution_time_ms=execution_time_ms,
            vector_search_time_ms=vector_search_time_ms,
            llm_time_ms=llm_time_ms,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return history
    
    async def get_query_history(
        self,
        project: ProjectConfig,
        limit: int = 50,
        offset: int = 0,
        success_only: Optional[bool] = None
    ) -> tuple[list[QueryHistory], int]:
        """
        Get query history for a project.
        
        Returns:
            Tuple of (queries, total_count)
        """
        query = QueryHistory.filter(project=project)
        
        if success_only is not None:
            query = query.filter(success=success_only)
        
        total = await query.count()
        queries = await query.offset(offset).limit(limit).order_by('-created_at')
        
        return queries, total
    
    async def get_query_by_id(self, query_id: UUID) -> Optional[QueryHistory]:
        """Get specific query by ID"""
        return await QueryHistory.get_or_none(id=query_id)
    
    async def get_project_stats(self, project: ProjectConfig) -> Dict[str, Any]:
        """Get statistics for a project"""
        total_queries = await QueryHistory.filter(project=project).count()
        successful_queries = await QueryHistory.filter(
            project=project, 
            success=True
        ).count()
        failed_queries = total_queries - successful_queries
        
        # Average execution time
        avg_time = await QueryHistory.filter(
            project=project,
            success=True
        ).all().values('execution_time_ms')
        
        avg_execution_time = 0
        if avg_time:
            avg_execution_time = sum(q['execution_time_ms'] for q in avg_time) // len(avg_time)
        
        return {
            'total_queries': total_queries,
            'successful_queries': successful_queries,
            'failed_queries': failed_queries,
            'success_rate': (successful_queries / total_queries * 100) if total_queries > 0 else 0,
            'avg_execution_time_ms': avg_execution_time
        }


# Global service instance
query_service = QueryService()
