from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ImageCreate(BaseModel):
    filename: str
    source: str


class ImageResponse(BaseModel):
    id: int
    uuid: str
    filename: str
    source: str
    is_face_detected: bool
    face_count: Optional[int]
    storage_path: str
    thumbnail_path: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ImageDetailResponse(ImageResponse):
    labels: List = []
    predictions: List = []
