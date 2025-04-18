from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.elastic import ElasticsearchManager
from app.api.search import router as search_router
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# In prod we can limit by specific address
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

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
    return {"status": "healthy"}
