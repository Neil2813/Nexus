"""Configuration management for NASA Space Biology Knowledge Engine.

Handles environment variables, service detection, and fallback configurations.
Ensures the application works in all environments with graceful degradation.
"""

import os
import logging
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support and sensible defaults."""
    
    # NASA OSDR API Configuration
    nasa_osdr_api_key: str = Field(
        default="VfaQ43NjOifLniAF7rXTQS1qys4Cl8uFWNM48hCe",
        description="NASA OSDR API key"
    )
    nasa_osdr_base_url: str = Field(
        default="https://osdr.nasa.gov",
        description="NASA OSDR base URL"
    )
    nasa_geode_base_url: str = Field(
        default="https://genelab-data.ndc.nasa.gov",
        description="NASA GeneLab/GEODE base URL"
    )
    # Additional NASA API endpoints for better coverage
    nasa_api_base_url: str = Field(
        default="https://api.nasa.gov",
        description="NASA API base URL"
    )
    nasa_genelab_base_url: str = Field(
        default="https://genelab.nasa.gov",
        description="NASA GeneLab base URL"
    )
    
    # AI Services (Optional)
    gemini_api_key: Optional[str] = Field(default=None, description="Google Gemini API key")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    
    # Database Configuration (Optional)
    redis_url: Optional[str] = Field(default=None, description="Redis connection URL")
    neo4j_uri: Optional[str] = Field(default=None, description="Neo4j connection URI")
    neo4j_user: str = Field(default="neo4j", description="Neo4j username")
    neo4j_password: Optional[str] = Field(default=None, description="Neo4j password")
    
    # Application Settings
    environment: str = Field(default="development", description="Environment (development/production)")
    debug: bool = Field(default=True, description="Enable debug mode")
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="CORS allowed origins (comma-separated)"
    )
    api_prefix: str = Field(default="/api", description="API route prefix")
    
    # Cache Settings
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")
    max_cache_size: int = Field(default=1000, description="Maximum cache size")
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, description="Rate limit requests per window")
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Data Directory
    data_dir: str = Field(default="./data", description="Data directory for local storage")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    def get_database_url(self) -> str:
        """Get database URL with fallback to SQLite."""
        if self.redis_url:
            return self.redis_url
        # Fallback to SQLite
        os.makedirs(self.data_dir, exist_ok=True)
        return f"sqlite:///{self.data_dir}/nexus.db"
    
    def has_redis(self) -> bool:
        """Check if Redis is configured."""
        return bool(self.redis_url)
    
    def has_neo4j(self) -> bool:
        """Check if Neo4j is configured."""
        return bool(self.neo4j_uri and self.neo4j_password)
    
    def has_gemini(self) -> bool:
        """Check if Gemini AI is configured."""
        return bool(self.gemini_api_key)
    
    def has_openai(self) -> bool:
        """Check if OpenAI is configured."""
        return bool(self.openai_api_key)


# Global settings instance
settings = Settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Create data directory if it doesn't exist
os.makedirs(settings.data_dir, exist_ok=True)

logger.info(f"NEXUS configuration loaded:")
logger.info(f"  - Environment: {settings.environment}")
logger.info(f"  - Debug: {settings.debug}")
logger.info(f"  - API Prefix: {settings.api_prefix}")
logger.info(f"  - Data Directory: {settings.data_dir}")
logger.info(f"  - Redis Available: {settings.has_redis()}")
logger.info(f"  - Neo4j Available: {settings.has_neo4j()}")
logger.info(f"  - Gemini AI Available: {settings.has_gemini()}")
logger.info(f"  - OpenAI Available: {settings.has_openai()}")

# Legacy compatibility constants (separate from settings object)
APP_NAME = "NASA Space Biology Knowledge Engine"
API_PREFIX = settings.api_prefix
OSDR_BASE = settings.nasa_osdr_base_url
GEMINI_API_KEY = settings.gemini_api_key
GEMINI_MODEL = "models/text-bison-001"
REDIS_URL = settings.redis_url
NEO4J_URL = settings.neo4j_uri
NEO4J_USER = settings.neo4j_user
NEO4J_PASSWORD = settings.neo4j_password
SQLITE_URL = f"sqlite:///{settings.data_dir}/nexus.db"
CACHE_TTL_SHORT = 300
CACHE_TTL_MED = settings.cache_ttl
CACHE_TTL_LONG = 3600
