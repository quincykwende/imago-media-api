from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    es_host: str
    es_user: str
    es_pass: str
    es_index: str = "imago"
    image_base_url: str = "https://www.picfy-images.de"
    verify_certs: bool = False
    ssl_show_warn: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()



