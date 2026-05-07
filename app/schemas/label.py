from pydantic import BaseModel
from typing import Optional
from app.models.label import SeasonEnum


class LabelCreate(BaseModel):
    season: SeasonEnum
    confidence: Optional[float] = None
    label_source: str = "human"
    labeled_by: Optional[str] = None
    notes: Optional[str] = None
    is_verified: bool = False


class LabelResponse(BaseModel):
    id: int
    image_id: int
    season: str
    confidence: Optional[float]
    label_source: str
    labeled_by: Optional[str]
    notes: Optional[str]
    is_verified: bool

    class Config:
        from_attributes = True
