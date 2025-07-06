from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Album(Base):
    __tablename__ = 'albums'

    id = Column(String, primary_key=True)  # Spotify album ID
    name = Column(String, nullable=False)
    artist_id = Column(String, ForeignKey('artists.id'), nullable=False)
    release_date = Column(String)
    total_tracks = Column(Integer)
    album_type = Column(String)  # e.g., 'album', 'single', 'compilation'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    artist = relationship("Artist", back_populates="albums")
    tracks = relationship("Track", back_populates="album")
