from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    listening_events = relationship("ListeningEvent", back_populates="user")
    playlists = relationship("Playlist", back_populates="user")
    genre_preferences = relationship("UserGenrePreference", back_populates="user")
    social_accounts = relationship(
        "SocialAccount", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )


    def __repr__(self) -> str:
        return f"<User(id='{self.id}', username='{self.username}')>"
