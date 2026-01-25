"""Application settings and environment configuration."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Supabase
    supabase_url: str
    supabase_key: str
    
    # Google Gemini
    google_api_key: str

    # SMTP Configuration
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_email: str = "theprateekdilaware@gmail.com"
    smtp_password: str = "uttkgurcrdshcjii"
    
    # Application
    app_host: str = "0.0.0.0"
    app_port: int = 8080
    debug: bool = True
    
    # Timezone
    default_timezone: str = "Asia/Kolkata"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()
