from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ScrapeJobCreate(BaseModel):
    source: str  # pinterest, reddit, google
    query: str
    target_season: str
    max_images: int = 50


class ScrapeJobResponse(BaseModel):
    id: int
    source: str
    query: str
    target_season: str
    status: str
    images_found: int
    images_saved: int
    images_skipped: int
    error_message: Optional[str]
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
