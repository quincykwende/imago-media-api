from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import ConnectionError as ESConnectionError
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class ElasticsearchManager:
    _client: AsyncElasticsearch | None = None

    @classmethod
    async def get_client(cls) -> AsyncElasticsearch:
        if cls._client is None:
            cls._client = AsyncElasticsearch(
                hosts=[settings.es_host],
                basic_auth=(settings.es_user, settings.es_pass),
                verify_certs=False,
                request_timeout=30,
                max_retries=3,
                retry_on_timeout=True
            )

            try:
                if not await cls._client.ping():
                    raise ESConnectionError("Failed to ping Elasticsearch")
                logger.info("Connected to Elasticsearch")
            except Exception as e:
                await cls.close()
                raise ESConnectionError(f"Connection failed: {str(e)}")

        return cls._client

    @classmethod
    async def close(cls):
        if cls._client:
            await cls._client.close()
            cls._client = None
