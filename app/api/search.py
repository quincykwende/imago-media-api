from fastapi import APIRouter, Depends, HTTPException, Query
from elasticsearch import AsyncElasticsearch
from app.db.elastic import ElasticsearchManager
from app.config import settings
from app.models.schemas import MediaItem, SearchResponse, MediaMetadata
from app.utils.media import generate_thumbnail_path
import logging
from typing import Optional

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/search", response_model=SearchResponse)
async def search_media(
    query: str = "*",
    size: int = Query(10, gt=0, le=100),
    page: int = Query(1, gt=0),
    es: AsyncElasticsearch = Depends(ElasticsearchManager.get_client)
) -> SearchResponse:

    """
    Search media with pagination and unique results per bildnummer
    """
    try:
        response = await es.search(
            index=settings.es_index,
            body={
                "query": {
                    "query_string": {
                        "query": query,
                        "analyze_wildcard": True,
                        "fields": ["suchtext", "fotografen"]
                    }
                },
                "collapse": {
                    "field": "bildnummer"
                },
                "sort": [{"datum": "desc"}],
                "from": (page - 1) * size,
                "size": size
            }
        )

        results = [
            MediaItem(
                id=hit["_id"],
                title=hit["_source"].get("suchtext", ""),
                image=generate_thumbnail_path(hit["_source"].get("db", "st"), hit["_source"].get("bildnummer", "")),
                metadata=MediaMetadata(
                    image_number=hit["_source"].get("bildnummer", ""),
                    date=hit["_source"].get("datum"),
                    photographer=hit["_source"].get("fotografen"),
                    dimensions=f"{hit['_source'].get('hoehe', '')}x{hit['_source'].get('breite', '')}",
                    db=hit["_source"].get("db", "st")
                )
            )
            for hit in response["hits"]["hits"]
        ]

        # Calculate next page if more results exist
        total_hits = response["hits"]["total"]["value"]
        next_page = page + 1 if (page * size) < total_hits else None

        return SearchResponse(
            count=total_hits,
            results=results,
            next_page=next_page
        )

    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(500, detail=str(e))
