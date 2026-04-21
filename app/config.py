from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    pythonpath: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int = Field(..., ge=0) 
    refresh_token_expire_days: int = Field(..., ge=0) 
    session_lifetime_days: int = Field(..., ge=0) 
    api_prefix: str
    db_engine: str
    database_url: str

    model_config = SettingsConfigDict(
        env_file='.env', 
        env_file_encoding='utf-8'
        )


settings = Settings()
