"""
Configuration settings for Interview Coach.
Uses Pydantic Settings for environment variable management.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional
import sys
import logging

# Use basic logging here since log_config might not be loaded yet
_logger = logging.getLogger("config")


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file='.env', 
        env_file_encoding='utf-8', 
        extra='ignore'
    )

    # Required Keys (Will raise error if missing)
    OPENAI_API_KEY: str = Field(..., description="OpenAI API Key is required")
    
    # Optional Keys
    OPENAI_API_BASE: Optional[str] = Field(None, description="Custom API Base URL")
    
    # Model Configurations
    MODEL_OBSERVER: str = "openai/gpt-4o"
    MODEL_INTERVIEWER: str = "openai/gpt-4o"
    MODEL_ROUTER: str = "openai/gpt-4o-mini"
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None  # Optional file logging


# Singleton instance
try:
    settings = Settings()
    _logger.debug("Configuration loaded successfully")
except Exception as e:
    _logger.error("Configuration Error: %s", e)
    print(f"Configuration Error: {e}")
    print("Please ensure .env file exists and contains OPENAI_API_KEY.")
    sys.exit(1)
