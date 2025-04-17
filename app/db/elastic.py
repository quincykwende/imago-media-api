from elasticsearch import AsyncElasticsearch
from app.config import settings

class ElasticsearchManager:
    _instance = None

    def __init__(self):
        if not ElasticsearchManager._instance:
            self.client = None

    @classmethod
    async def get_client(cls):
        if not cls._instance:
            cls._instance = AsyncElasticsearch(
                hosts=[settings.es_host],
                basic_auth=(settings.es_user, settings.es_pass),
                ssl_show_warn=False,
                verify_certs=False,
                max_retries=3,
                timeout=30,
                connections_per_node=20
            )
        return cls._instance

    @classmethod
    async def close(cls):
        if cls._instance:
            await cls._instance.close()
            cls._instance = None
