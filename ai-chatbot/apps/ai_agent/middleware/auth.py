"""
Authentication middleware for API key validation
"""
from fastapi import Request, HTTPException, status
from fastapi.security import APIKeyHeader
from typing import Optional
import logging

from apps.ai_agent.models import ProjectConfig

logger = logging.getLogger(__name__)

# API Key header scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class APIKeyAuth:
    """Dependency for API key authentication"""
    
    async def __call__(self, api_key: Optional[str] = None) -> ProjectConfig:
        """
        Validate API key and return associated project.
        
        Args:
            api_key: API key from X-API-Key header
            
        Returns:
            ProjectConfig instance
            
        Raises:
            HTTPException: If API key is invalid or missing
        """
        if not api_key:
            logger.warning("API key missing from request")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required. Include 'X-API-Key' header.",
                headers={"WWW-Authenticate": "ApiKey"},
            )
        
        # Validate API key format
        if not api_key.startswith("sk_proj_"):
            logger.warning(f"Invalid API key format: {api_key[:10]}...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key format",
            )
        
        # Look up project by API key
        project = await ProjectConfig.get_or_none(
            api_key=api_key,
            is_active=True
        )
        
        if not project:
            logger.warning(f"Invalid or inactive API key: {api_key[:10]}...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or inactive API key",
            )
        
        logger.info(f"Authenticated request for project: {project.name}")
        return project


# Global auth dependency instance
require_api_key = APIKeyAuth()


async def get_project_from_api_key(api_key: str = api_key_header) -> ProjectConfig:
    """
    FastAPI dependency to get project from API key.
    
    Usage:
        @router.get("/endpoint")
        async def endpoint(project: ProjectConfig = Depends(get_project_from_api_key)):
            ...
    """
    return await require_api_key(api_key)
