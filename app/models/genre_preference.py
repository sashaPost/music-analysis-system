from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.database import Base


class UserGenrePreference(Base):
    """Track user's genre preferences over time"""
    __tablename__ = 'user_genre_preferences'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    genre = Column(String, nullable=False)
    preference_score = Column(Float, default=0.0)  # Score indicating preference strength
    period = Column(String, nullable=False)  
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="genre_preferences")

    __table_args__ = (Index("ix_user_genre", "user_id", "genre"),)
