from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class RefreshToken(Base):
    __tablename__ = "refresh_token"

    refresh_token = Column(UUID, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
