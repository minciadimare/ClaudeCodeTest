from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime


class PredictionResponse(BaseModel):
    id: int
    image_id: int
    model_version: str
    predicted_season: str
    confidence: float
    probabilities: str  # JSON string
    inference_method: str
    latency_ms: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class ClassifyResponse(BaseModel):
    prediction_uuid: str
    season: str
    confidence: float
    probabilities: Dict[str, float]
    inference_method: str
