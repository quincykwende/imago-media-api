from fastapi import FastAPI
from app.db.elastic import ElasticsearchManager
from app.api.search import router as search_router
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(search_router, prefix="/api/v1")

@app.on_event("startup")
async def startup():
    try:
        await ElasticsearchManager.get_client()
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown():
    await ElasticsearchManager.close()

@app.get("/health")
async def health_check():
    try:
        if await ElasticsearchManager.get_client().ping():
            return {"status": "healthy"}
    except Exception:
        pass
    return {"status": "unhealthy"}
