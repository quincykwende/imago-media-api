from fastapi import APIRouter, Depends, HTTPException, Query
from elasticsearch import AsyncElasticsearch
from app.db.elastic import ElasticsearchManager
from app.config import settings
from app.models.schemas import MediaItem, SearchResponse
from app.utils.media import generate_thumbnail_path, extract_copyright
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

async def execute_es_search(
    es: AsyncElasticsearch,
    query: str,
    page: int,
    size: int
) -> dict:
    """Execute Elasticsearch query with pagination"""
    return await es.search(
        index=settings.es_index,
        body={
            "query": {
                "query_string": {
                    "query": query,
                    "analyze_wildcard": True,
                    "fields": ["suchtext^3", "fotografen^2"]
                }
            },
            "collapse": {"field": "bildnummer"},
            "sort": [{"datum": {"order": "desc"}}],
            "from": (page - 1) * size,
            "size": size
        }
    )

def process_search_hit(hit: dict) -> MediaItem:
    """Transform Elasticsearch hit into MediaItem"""
    source = hit["_source"]
    bildnummer = source.get("bildnummer", "")

    return MediaItem(
        id=hit["_id"],
        title=source.get("suchtext", ""),
        image=generate_thumbnail_path(
            source.get("db", "st"),
            bildnummer
        ),
        metadata={
            "image_number": bildnummer,
            "date": source.get("datum"),
            "photographer": source.get("fotografen"),
            "width": source.get("breite"),
            "height": source.get("hoehe"),
            "copyright": extract_copyright(source.get("suchtext", "")),
            "db": source.get("db", "st")
        }
    )

@router.get("/search", response_model=SearchResponse)
async def search_media(
    query: str = Query("*", min_length=1),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    es: AsyncElasticsearch = Depends(ElasticsearchManager.get_client)
) -> SearchResponse:
    """Search media endpoint with pagination"""
    try:
        response = await execute_es_search(es, query, page, size)
        total_results = response["hits"]["total"]["value"]

        return SearchResponse(
            count=total_results,
            results=[process_search_hit(hit) for hit in response["hits"]["hits"]],
            next_page=page + 1 if page * size < total_results else None
        )

    except Exception as e:
        logger.error(f"Search failed: {str(e)}", exc_info=True)
        raise HTTPException(500, detail="Internal server error")
