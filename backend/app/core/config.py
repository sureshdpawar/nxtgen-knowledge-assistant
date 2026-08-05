from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    LLM_API: str
    LLM_API_KEY: str

    SECRET_KEY: str
    ALGORITHM: str

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


settings = Settings()