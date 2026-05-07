from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import uuid


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, nullable=False, default=lambda: str(uuid.uuid4()), index=True)
    filename = Column(String, nullable=False)
    original_url = Column(String, nullable=True)
    source = Column(String, nullable=False)  # scraped_pinterest, scraped_reddit, scraped_google, manual_upload
    file_hash = Column(String, unique=True, nullable=False, index=True)  # SHA-256
    file_size_bytes = Column(Integer, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    format = Column(String, nullable=True)  # JPEG, PNG, WEBP
    is_face_detected = Column(Boolean, default=False, nullable=False)
    face_count = Column(Integer, nullable=True)
    storage_path = Column(String, nullable=False)  # relative path under storage/images/
    thumbnail_path = Column(String, nullable=True)  # relative path to 224x224 thumbnail
    scrape_job_id = Column(Integer, ForeignKey("scrape_jobs.id"), nullable=True)
    split = Column(String, nullable=True)  # train, val, test
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=func.now(), nullable=False)

    labels = relationship("Label", back_populates="image", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="image", cascade="all, delete-orphan")
    scrape_job = relationship("ScrapeJob", back_populates="images")
