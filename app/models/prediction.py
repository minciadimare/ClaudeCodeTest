from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id", ondelete="CASCADE"), nullable=False, index=True)
    model_version = Column(String, nullable=False)  # e.g. efficientnet-b0-v1.2
    predicted_season = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)  # top-1 probability
    probabilities = Column(String, nullable=False)  # JSON string
    inference_method = Column(String, nullable=False)  # pytorch, rule_based
    latency_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    image = relationship("Image", back_populates="predictions")
