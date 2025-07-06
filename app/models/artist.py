from sqlalchemy import Column, String, Integer, DateTime, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Artist(Base):
    __tablename__ = 'artists'

    id = Column(String, primary_key=True)
    name = Column(String, index=True, nullable=False)
    genres = Column(ARRAY(String), default=[])
    popularity = Column(Integer, default=0)
    followers = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    albums = relationship("Album", back_populates="artist")
    tracks = relationship("Track", back_populates="artist")    
