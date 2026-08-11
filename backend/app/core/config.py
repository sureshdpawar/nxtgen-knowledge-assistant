from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    DATABASE_URL: str

    LLM_API: str
    LLM_API_KEY: str
    
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

    STORAGE_PATH: str = str(BASE_DIR / "storage")
    
    DOCUMENT_STORAGE_PATH: str = "./storage"
    
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    TOP_K: int = 5
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive="ignore",
    )


settings = Settings()