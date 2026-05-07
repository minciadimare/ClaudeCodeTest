from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class ScrapeJob(Base):
    __tablename__ = "scrape_jobs"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False)  # pinterest, reddit, google
    query = Column(String, nullable=False)
    target_season = Column(String, nullable=False)
    status = Column(String, default="pending", nullable=False)  # pending, running, done, failed
    images_found = Column(Integer, default=0, nullable=False)
    images_saved = Column(Integer, default=0, nullable=False)
    images_skipped = Column(Integer, default=0, nullable=False)  # dedup skips
    error_message = Column(String, nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    images = relationship("Image", back_populates="scrape_job")
