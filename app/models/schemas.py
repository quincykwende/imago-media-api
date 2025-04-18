from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MediaMetadata(BaseModel):
    image_number: str
    date: Optional[datetime] = None
    photographer: Optional[str] = None
    dimensions: Optional[str] = None
    copyright: Optional[str] = None
    db: str

class MediaItem(BaseModel):
    id: str
    title: str
    thumbnail: str
    metadata: MediaMetadata

class SearchResponse(BaseModel):
    count: int
    results: list[MediaItem]
    next_page: Optional[int] = None
