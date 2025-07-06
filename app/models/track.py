from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Track(Base):
    __tablename__ = 'tracks'

    id = Column(String, primary_key=True)  # Spotify track ID
    name = Column(String, nullable=False)
    artist_id = Column(String, ForeignKey('artists.id'), nullable=False)
    album_id = Column(String, ForeignKey('albums.id'), nullable=False)
    duration_ms = Column(Integer, nullable=False)  # Duration in milliseconds
    popularity = Column(Integer, default=0)
    explicit = Column(Boolean, default=False)  # Explicit content

    # Audio features (from Spotify API)
    acousticness = Column(Float)
    danceability = Column(Float)
    energy = Column(Float)
    instrumentalness = Column(Float)
    liveness = Column(Float)
    loudness = Column(Float)
    speechiness = Column(Float)
    tempo = Column(Float)
    valence = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    artist = relationship("Artist", back_populates="tracks")
    album = relationship("Album", back_populates="tracks")
    listening_events = relationship("ListeningEvent", back_populates="track")
    playlists = relationship("Playlist", secondary="playlist_track_association", back_populates="tracks")
