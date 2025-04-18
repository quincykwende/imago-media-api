from elasticsearch import AsyncElasticsearch
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class ElasticsearchManager:
    _client: AsyncElasticsearch = None

    @classmethod
    async def get_client(cls) -> AsyncElasticsearch:
        """Get singleton Elasticsearch client with connection pooling"""
        if cls._client is None:
            cls._client = AsyncElasticsearch(
                hosts=[settings.es_host],
                basic_auth=(settings.es_user, settings.es_pass),
                verify_certs=settings.verify_certs,
                ssl_show_warn=settings.ssl_show_warn,
                max_retries=3,
                retry_on_timeout=True,
                request_timeout=30
            )
            if not await cls._client.ping():
                raise ConnectionError("Failed to connect to Elasticsearch")
            logger.info("Elasticsearch connection established")
        return cls._client

    @classmethod
    async def close(cls):
        """Close connection pool"""
        if cls._client:
            await cls._client.close()
            cls._client = None
            logger.info("Elasticsearch connection closed")
