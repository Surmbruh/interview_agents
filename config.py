from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # Required Keys (Will raise error if missing)
    OPENAI_API_KEY: str = Field(..., description="OpenAI API Key is required")
    
    # Optional Keys
    OPENAI_API_BASE: Optional[str] = Field(None, description="Custom API Base URL")
    
    # Model Configurations
    MODEL_OBSERVER: str = "openai/gpt-4o"
    MODEL_INTERVIEWER: str = "openai/gpt-4o"
    MODEL_ROUTER: str = "openai/gpt-4o-mini"
    
    # App Settings
    LOG_FILE: str = "interview_log.json"

# Singleton instance
try:
    settings = Settings()
except Exception as e:
    print(f"❌ Configuration Error: {e}")
    print("Please ensure .env file exists and contains OPENAI_API_KEY.")
    import sys
    sys.exit(1)
