from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

class MediaMetadata(BaseModel):
    image_id: str
    date: Optional[datetime] = None
    photographer: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    copyright: Optional[str] = None

    @field_validator('width', 'height', mode='before')
    def parse_dimensions(cls, value):
        try:
            return int(value) if value else None
        except ValueError:
            return None

class MediaItem(BaseModel):
    id: str
    title: str
    image: str
    metadata: MediaMetadata

class SearchResponse(BaseModel):
    count: int
    results: list[MediaItem]
    next_page: Optional[int] = None
