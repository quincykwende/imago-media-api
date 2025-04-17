from pydantic import BaseSettings

class Settings(BaseSettings):
    es_host: str
    es_user: str
    es_pass: str
    es_index: str = "indexing"

    class Config:
        env_file = ".env"
        env_prefix = "ES_"
        case_sensitive = True

settings = Settings()
