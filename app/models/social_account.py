from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class SocialAccount(Base):
    __tablename__ = "social_accounts"

    id = Column(String, primary_key=True, index=True)
    provider = Column(String, nullable=False)
    provider_user_id = Column(String, nullable=False, index=True)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="social_accounts")
