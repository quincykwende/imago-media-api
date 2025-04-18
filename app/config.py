from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    es_host: str
    es_user: str
    es_pass: str
    es_index: str
    image_base_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="ES_",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
