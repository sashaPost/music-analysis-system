from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class ListeningEvent(Base):
    __tablename__ = 'listening_events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    track_id = Column(String, ForeignKey("tracks.id"), nullable=False)

    # Listening details
    played_at = Column(DateTime(timezone=True), nullable=False)
    duration_ms = Column(Integer, nullable=False)  # Duration of the listening event in milliseconds
    progress_ms = Column(Integer, nullable=False)  # How far into the track
    skipped = Column(Boolean, default=False)  # Whether the track was skipped

    # Context 
    context_type = Column(String, nullable=True)  # playlist, album, artist, etc.
    context_id = Column(String, nullable=True)  # ID of the context (e.g., playlist ID)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="listening_events")
    track = relationship("Track", back_populates="listening_events")
