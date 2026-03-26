"""
Configuration management using Pydantic settings
"""

import os
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load .env file manually
load_dotenv()

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Azure AD Configuration
    azure_client_id: str = Field(default_factory=lambda: os.getenv("AZURE_BACKEND_ENTRA_APP_CLIENT_ID", ""))
    azure_client_secret: str = Field(default_factory=lambda: os.getenv("AZURE_BACKEND_ENTRA_APP_CLIENT_SECRET", ""))
    azure_frontend_client_id: str = Field(default_factory=lambda: os.getenv("AZURE_FRONTEND_ENTRA_CLIENT_ID", ""))
    azure_frontend_client_secret: str = Field(default_factory=lambda: os.getenv("AZURE_FRONTEND_ENTRA_CLIENT_SECRET", ""))
    azure_tenant_id: str = Field(default_factory=lambda: os.getenv("AZURE_BACKEND_ENTRA_APP_TENANT_ID", ""))
    azure_authority: str = Field(default_factory=lambda: os.getenv("AZURE_AUTHORITY", "https://login.microsoftonline.com/"))
    azure_scopes: str = Field(default_factory=lambda: os.getenv("AZURE_SCOPES", "api://your-backend-app-id/access_as_user"))
    azure_use_obo: bool = Field(default_factory=lambda: os.getenv("AZURE_USE_OBO", "True").lower() == "true")
    
    # Azure AI Search - Using Managed Identity (RBAC)
    azure_search_endpoint: str = Field("", env="AZURE_SEARCH_ENDPOINT")
    # DEPRECATED: azure_search_key is no longer used with Managed Identity
    # azure_search_key: str = Field("", env="AZURE_SEARCH_KEY")
    azure_search_index_name: str = Field("droitai-index", env="AZURE_SEARCH_INDEX_NAME")
    
    # Azure OpenAI
    azure_openai_endpoint: str = Field("", env="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: str = Field("", env="AZURE_OPENAI_KEY")
    azure_openai_deployment_name: str = Field("gpt-4", env="AZURE_OPENAI_DEPLOYMENT_NAME")
    azure_openai_embedding_deployment: str = Field("text-embedding-ada-002", env="AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    
    # Azure Document Intelligence
    azure_doc_intelligence_endpoint: Optional[str] = Field(None, env="AZURE_DOC_INTELLIGENCE_ENDPOINT")
    azure_doc_intelligence_key: Optional[str] = Field(None, env="AZURE_DOC_INTELLIGENCE_KEY")
    
    # Azure Content Safety
    azure_content_safety_endpoint: Optional[str] = Field(None, env="AZURE_CONTENT_SAFETY_ENDPOINT")
    azure_content_safety_key: Optional[str] = Field(None, env="AZURE_CONTENT_SAFETY_KEY")
    
    # Azure Cosmos DB
    cosmos_db_endpoint: Optional[str] = Field(None, env="COSMOS_DB_ENDPOINT")
    cosmos_db_key: Optional[str] = Field(None, env="COSMOS_DB_KEY")
    cosmos_db_database_name: str = Field("rag-chat", env="COSMOS_DB_DATABASE_NAME")
    cosmos_db_container_name: str = Field("chat-history", env="COSMOS_DB_CONTAINER_NAME")
    
    # Azure Storage
    azure_storage_account_name: str = Field("", env="AZURE_STORAGE_ACCOUNT_NAME")
    azure_storage_account_key: str = Field("", env="AZURE_STORAGE_ACCOUNT_KEY")
    azure_storage_connection_string: str = Field("", env="AZURE_STORAGE_CONNECTION_STRING")
    azure_storage_container_name: str = Field("documents", env="AZURE_STORAGE_CONTAINER_NAME")
    
    # Application Configuration
    frontend_url: str = Field("http://localhost:3000", env="FRONTEND_URL")
    backend_url: str = Field("http://localhost:8000", env="BACKEND_URL")
    backend_internal_url: str = Field("http://backend:8000", env="BACKEND_INTERNAL_URL")
    
    # Feature Toggles
    enable_local_parsing: bool = Field(False, env="ENABLE_LOCAL_PARSING")
    enable_azure_doc_intelligence: bool = Field(True, env="ENABLE_AZURE_DOC_INTELLIGENCE")
    enable_content_safety: bool = Field(True, env="ENABLE_CONTENT_SAFETY")
    enable_detailed_logging: bool = Field(False, env="ENABLE_DETAILED_LOGGING")
    enable_metrics: bool = Field(True, env="ENABLE_METRICS")
    
    # Azure Monitoring Configuration
    application_insights_connection_string: Optional[str] = Field(None, env="APPLICATIONINSIGHTS_CONNECTION_STRING")
    log_analytics_workspace_id: Optional[str] = Field(None, env="LOG_ANALYTICS_WORKSPACE_ID")
    
    # Local Development
    local_docs_path: str = Field("./data/raw", env="LOCAL_DOCS_PATH")
    local_processed_path: str = Field("./data/processed", env="LOCAL_PROCESSED_PATH")
    redis_password: str = Field("redis123", env="REDIS_PASSWORD")
    cosmos_db_emulator: bool = Field(False, env="COSMOS_DB_EMULATOR")
    
    # Security
    jwt_secret_key: str = Field("dev-secret-key-change-in-production", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field("HS256", env="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(24, env="JWT_EXPIRATION_HOURS")
    
    # CORS
    allowed_origins: str = Field("http://localhost:3000", env="ALLOWED_ORIGINS")
    allowed_methods: str = Field("GET,POST,PUT,DELETE,OPTIONS", env="ALLOWED_METHODS")
    allowed_headers: str = Field("Content-Type,Authorization", env="ALLOWED_HEADERS")
    
    # Environment
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("info", env="LOG_LEVEL")
    
    # Cache Configuration
    cache_ttl_seconds: int = Field(3600, env="CACHE_TTL_SECONDS")
    embedding_cache_size: int = Field(1000, env="EMBEDDING_CACHE_SIZE")
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.debug or self.log_level.lower() == "debug"
    
    def __post_init__(self):
        """Validate critical security settings"""
        if self.jwt_secret_key == "your-jwt-secret-key":
            raise ValueError(
                "JWT_SECRET_KEY cannot be the default value. "
                "Please set a secure secret key in your environment variables."
            )
        
        if len(self.jwt_secret_key) < 32:
            raise ValueError(
                "JWT_SECRET_KEY must be at least 32 characters long for security."
            )
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Convert comma-separated origins to list"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    @property
    def allowed_methods_list(self) -> List[str]:
        """Convert comma-separated methods to list"""
        return [method.strip() for method in self.allowed_methods.split(",")]
    
    @property
    def allowed_headers_list(self) -> List[str]:
        """Convert comma-separated headers to list"""
        return [header.strip() for header in self.allowed_headers.split(",")]


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get global settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings():
    """Reload settings from environment"""
    global _settings
    _settings = Settings()
