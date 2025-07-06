from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


playlist_track_association = Table(
    'playlist_track_association', Base.metadata,
    Column('playlist_id', String, ForeignKey('playlists.id')),
    Column('track_id', String, ForeignKey('tracks.id')),
)


class Playlist(Base):
    __tablename__ = 'playlists'

    id = Column(String, primary_key=True)  # Spotify playlist ID
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    public = Column(Boolean, default=False)
    collaborative = Column(Boolean, default=False)
    total_tracks = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="playlists")
    tracks = relationship(
        "Track", 
        secondary=playlist_track_association, 
        back_populates="playlists"
    )
