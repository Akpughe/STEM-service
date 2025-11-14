"""Application settings using Pydantic."""
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Allow extra fields in .env file
    )
    
    # Wolfram Alpha API Configuration
    wolfram_app_id: str = Field(default="YA86XKTQWK", description="Wolfram Alpha App ID")
    wolfram_llm_api_url: str = Field(
        default="https://api.wolframalpha.com/v1/llm-api",
        description="Wolfram LLM API endpoint"
    )
    wolfram_full_results_api_url: str = Field(
        default="https://api.wolframalpha.com/v2/query",
        description="Wolfram Full Results API endpoint"
    )
    wolfram_show_steps_api_url: str = Field(
        default="https://api.wolframalpha.com/v2/query",
        description="Wolfram Show Steps API endpoint"
    )
    wolfram_language_api_url: str = Field(
        default="https://api.wolframalpha.com/v1/query",
        description="Wolfram Language API endpoint"
    )
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., description="OpenAI API key")
    openai_model: str = Field(
        default="gpt-4o",
        description="OpenAI model to use"
    )
    openai_max_completion_tokens: int = Field(
        default=4096,
        description="Maximum completion tokens for OpenAI responses"
    )

    # Groq Configuration
    groq_api_key: str = Field(..., description="Groq API key")
    groq_model: str = Field(
        default="openai/gpt-oss-120b",
        description="Groq model to use (openai/gpt-oss-120b for math reasoning)"
    )
    groq_max_completion_tokens: int = Field(
        default=8192,
        description="Maximum completion tokens for Groq responses"
    )
    
    # Redis Configuration
    redis_url: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL"
    )
    redis_ttl: int = Field(
        default=3600,
        description="Default TTL for cached items in seconds"
    )
    
    # Server Configuration
    server_host: str = Field(default="0.0.0.0", description="Server host", validation_alias="HOST")
    server_port: int = Field(default=8000, description="Server port", validation_alias="PORT")
    debug: bool = Field(default=False, description="Debug mode")
    
    # CORS Configuration
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001", "http://localhost:7860"],
        description="Allowed CORS origins"
    )
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    sentry_dsn: Optional[str] = Field(default=None, description="Sentry DSN")
    
    # File Upload
    max_file_size: int = Field(
        default=10485760,  # 10MB
        description="Maximum file size in bytes"
    )
    allowed_image_types: List[str] = Field(
        default=["image/jpeg", "image/png", "image/gif", "image/webp"],
        description="Allowed image MIME types"
    )


# Create settings instance
settings = Settings()
