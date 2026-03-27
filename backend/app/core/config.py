"""
Configuration management using Pydantic settings
Aligned with DroitAI azd environment variables
"""

import os
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Core Azure Environment
    azure_env_name: str = Field(default_factory=lambda: os.getenv("AZURE_ENV_NAME", "droitaienv"))
    azure_subscription_id: str = Field(default_factory=lambda: os.getenv("AZURE_SUBSCRIPTION_ID", ""))
    
    # Azure AI Search (Matches your azd outputs)
    azure_search_endpoint: str = Field(default_factory=lambda: os.getenv("AZURE_SEARCH_ENDPOINT", ""))
    azure_search_key: str = Field(default_factory=lambda: os.getenv("AZURE_SEARCH_KEY", ""))
    azure_search_index: str = Field(default_factory=lambda: os.getenv("AZURE_SEARCH_INDEX_NAME", "droitai-search-index"))

    # Azure OpenAI (Check your ai-services.bicep outputs)
    azure_openai_endpoint: str = Field(default_factory=lambda: os.getenv("AZURE_OPENAI_ENDPOINT", ""))
    azure_openai_api_key: str = Field(default_factory=lambda: os.getenv("AZURE_OPENAI_API_KEY", ""))
    azure_openai_chat_deployment: str = Field(default_factory=lambda: os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-4o"))
    azure_openai_embedding_deployment: str = Field(default_factory=lambda: os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002"))

    # Azure Storage
    azure_storage_account: str = Field(default_factory=lambda: os.getenv("AZURE_STORAGE_ACCOUNT_NAME", ""))
    azure_storage_container: str = Field(default_factory=lambda: os.getenv("AZURE_STORAGE_CONTAINER_NAME", "documents"))

    # Azure Document Intelligence
    azure_doc_intel_endpoint: str = Field(default_factory=lambda: os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT", ""))

    # Entra ID / Auth (Using your provided Client IDs)
    azure_client_id: str = Field(default_factory=lambda: os.getenv("BACKEND_CLIENT_ID", "e155cc3c-4389-44d5-a5b1-e3866a4985a2"))
    azure_client_secret: str = Field(default_factory=lambda: os.getenv("BACKEND_CLIENT_SECRET", ""))
    azure_frontend_client_id: str = Field(default_factory=lambda: os.getenv("FRONTEND_CLIENT_ID", "e155cc3c-4389-44d5-a5b1-e3866a4985a2"))
    azure_frontend_client_secret: str = Field(default_factory=lambda: os.getenv("FRONTEND_CLIENT_SECRET", ""))
    azure_tenant_id: str = Field(default_factory=lambda: os.getenv("AZURE_TENANT_ID", ""))
    
    # App Settings
    jwt_secret_key: str = Field(default="replace-with-secure-key-for-production")
    allowed_origins: str = "*"
    allowed_methods: str = "GET,POST,PUT,DELETE,OPTIONS"
    allowed_headers: str = "Content-Type,Authorization"
    
    # Azure Monitoring Configuration
    application_insights_connection_string: Optional[str] = Field(None, env="APPLICATIONINSIGHTS_CONNECTION_STRING")
    azure_log_analytics_workspace_id: Optional[str] = Field(None, env="AZURE_LOG_ANALYTICS_WORKSPACE_ID")
    
    # Service Configuration
    document_intelligence_model: str = Field(default="prebuilt-layout")
    search_semantic_config: str = Field(default="legal-semantic-config")
    search_top_k: int = Field(default=5)
    openai_max_tokens: int = Field(default=800)
    
    # Feature Flags
    enable_content_safety: bool = Field(default=True)
    enable_local_parsing: bool = Field(default=False)
    enable_azure_doc_intelligence: bool = Field(default=True)
    
    def __post_init__(self):
        """Validate critical environment variables"""
        required_vars = [
            (self.azure_search_endpoint, "AZURE_SEARCH_ENDPOINT"),
            (self.azure_openai_endpoint, "AZURE_OPENAI_ENDPOINT"),
            (self.azure_doc_intel_endpoint, "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"),
            (self.azure_storage_account, "AZURE_STORAGE_ACCOUNT_NAME")
        ]
        
        missing_vars = [var_name for value, var_name in required_vars if not value]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        if self.jwt_secret_key == "replace-with-secure-key-for-production":
            raise ValueError("JWT_SECRET_KEY must be set to a secure value for production")
    
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
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
