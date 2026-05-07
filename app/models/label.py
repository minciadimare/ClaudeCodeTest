from enum import Enum
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class SeasonEnum(str, Enum):
    # Winter
    COOL_WINTER = "Cool Winter"
    DEEP_WINTER = "Deep Winter"
    BRIGHT_WINTER = "Bright Winter"
    TRUE_WINTER = "True Winter"

    # Spring
    BRIGHT_SPRING = "Bright Spring"
    LIGHT_SPRING = "Light Spring"
    WARM_SPRING = "Warm Spring"
    TRUE_SPRING = "True Spring"

    # Autumn
    WARM_AUTUMN = "Warm Autumn"
    DEEP_AUTUMN = "Deep Autumn"
    SOFT_AUTUMN = "Soft Autumn"
    TRUE_AUTUMN = "True Autumn"

    # Summer
    SOFT_SUMMER = "Soft Summer"
    LIGHT_SUMMER = "Light Summer"
    COOL_SUMMER = "Cool Summer"
    TRUE_SUMMER = "True Summer"


class Label(Base):
    __tablename__ = "labels"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id", ondelete="CASCADE"), nullable=False, index=True)
    season = Column(String, nullable=False)  # stores SeasonEnum value
    confidence = Column(Float, nullable=True)  # 0.0-1.0, None if human-labeled with certainty
    label_source = Column(String, nullable=False)  # human, keyword_inferred, model, claude_api
    labeled_by = Column(String, nullable=True)  # admin username if human
    notes = Column(String, nullable=True)  # free text notes from labeler
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=func.now(), nullable=False)

    image = relationship("Image", back_populates="labels")
