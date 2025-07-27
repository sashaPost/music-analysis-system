from sqlalchemy import Column, String, ForeignKey, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base

class SocialAccount(Base):
    __tablename__ = "social_accounts"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    provider = Column(String, nullable=False)
    provider_user_id = Column(String, nullable=False, index=True)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="social_accounts")
