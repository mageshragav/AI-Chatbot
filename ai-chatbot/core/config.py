# core/config.py
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Database
    DATABASE_URL: str = "postgres://user:password@localhost:5432/ai_chatbot"
    
    # AI/LangChain Configuration
    AI_API_KEY: str = "dummy-key-for-migrations"  # Override in .env
    AI_API_BASE_URL: str = "https://api.openai.com/v1"
    AI_MODEL: str = "gpt-4o-mini"
    AI_TEMPERATURE: float = 0.3
    AI_MAX_TOKENS: int = 1000
    AI_TIMEOUT: int = 30
    
    # Vector Store Configuration
    CHROMA_PERSIST_DIR: str = "./chroma_data"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    VECTOR_SEARCH_TOP_K: int = 5
    
    # API Configuration
    API_TITLE: str = "AI Agent - Django ORM Query Generator"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Convert natural language to Django ORM queries"
    API_RATE_LIMIT: int = 100  # requests per minute per project
    API_TIMEOUT: int = 30
    
    # Cache Configuration (Redis)
    REDIS_URL: Optional[str] = None
    CACHE_TTL: int = 3600  # 1 hour
    CACHE_ENABLED: bool = False
    
    # Security
    ALLOWED_ORIGINS: List[str] = ["*"]
    API_KEY_PREFIX: str = "sk_proj_"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # "json" or "text"
    
    # Agent Configuration
    AGENT_TOOL_CALL_LIMIT: int = 7
    AGENT_MODEL_CALL_LIMIT: int = 7
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

# Tortoise ORM Configuration
TORTOISE_ORM = {
    "connections": {"default": settings.DATABASE_URL},
    "apps": {
        "models": {
            "models": [
                "apps.ai_agent.models",
                "aerich.models",  # Required for Aerich
            ],
            "default_connection": "default",
        }
    },
}