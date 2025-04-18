from fastapi import APIRouter, Depends, HTTPException, Query
from elasticsearch import AsyncElasticsearch
from app.db.elastic import ElasticsearchManager
from app.config import settings
from app.models.schemas import MediaItem, SearchResponse
from app.utils.media import generate_thumbnail_path, extract_copyright
from datetime import datetime
from typing import Optional, List
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

async def execute_es_search(
    es: AsyncElasticsearch,
    query: str,
    photographer: Optional[str],
    from_date: Optional[datetime],
    to_date: Optional[datetime],
    page: int,
    size: int
) -> dict:
    """Build & execute Elasticsearch query"""
    try:
        # Build base query
        query_body = {
            "query": {
                "bool": {
                    "must": [{
                        "query_string": {
                            "query": query,
                            "fields": ["suchtext^3", "fotografen^2"],
                            "analyze_wildcard": True,
                            "default_operator": "AND"
                        }
                    }],
                    "filter": []
                }
            },
            "collapse": {
                "field": "bildnummer",
                "inner_hits": {
                    "name": "latest",
                    "size": 1,
                    "sort": [{"datum": "desc"}]
                }
            },
            "track_total_hits": True,
            "from": (page - 1) * size,
            "size": size
        }

        # photographer filter
        if photographer:
            query_body["query"]["bool"]["filter"].append({
                "query_string": {
                    "query": f"fotografen:*{photographer}*",
                }
            })

        # Date range filter
        if from_date or to_date:
            date_range = {}
            if from_date:
                date_range["gte"] = from_date.isoformat()
            if to_date:
                date_range["lte"] = to_date.isoformat()

            query_body["query"]["bool"]["filter"].append({
                "range": {"datum": date_range}
            })

        return await es.search(index=settings.es_index, body=query_body, request_timeout=30)

    except ValueError as ve:
        logger.warning(f"Invalid query parameters: {str(ve)}")
        raise HTTPException(422, detail=str(ve))
    except Exception as e:
        logger.error(f"Search execution failed: {str(e)}")
        raise

def process_search_hit(hit: dict) -> MediaItem:
    """hit processing"""
    source = hit["_source"]
    inner_hit = hit.get("inner_hits", {}).get("latest", {}).get("hits", {}).get("hits", [{}])[0]
    latest_source = inner_hit.get("_source", source)

    bildnummer = latest_source.get("bildnummer", "")

    return MediaItem(
        id=hit["_id"],
        title=latest_source.get("suchtext", ""),
        image=generate_thumbnail_path(latest_source.get("db", "st"), bildnummer),
        metadata={
            "image_id": bildnummer,
            "date": latest_source.get("datum"),
            "photographer": latest_source.get("fotografen"),
            "width": latest_source.get("breite"),
            "height": latest_source.get("hoehe"),
            "copyright": extract_copyright(latest_source.get("suchtext", ""))
        }
    )

@router.get("/search", response_model=SearchResponse)
async def search_media(
    query: str = Query("*", min_length=1),
    photographer: Optional[str] = Query(None, min_length=2),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None, description="End date must be after start date"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    es: AsyncElasticsearch = Depends(ElasticsearchManager.get_client)
) -> SearchResponse:
    """Search endpoint"""
    try:
        # Date validation
        if from_date and to_date and from_date > to_date:
            raise HTTPException(422, detail="End date must be after start date")

        response = await execute_es_search(es, query, photographer, from_date, to_date, page, size)

        total = response["hits"]["total"]["value"]
        results = [process_search_hit(hit) for hit in response["hits"]["hits"]]
        next_page = page + 1 if page * size < total else None

        return SearchResponse(count=total, results=results, next_page=next_page)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search failed: {str(e)}", exc_info=True)
        raise HTTPException(500, detail="Internal server error")
