from sqlalchemy import Boolean, Column, Integer, LargeBinary, SmallInteger

from app.database import Base


class TelegramAccount(Base):
    __tablename__ = "telegram_account"

    id = Column(Integer, primary_key=True)
    auth_key = Column(LargeBinary(256), nullable=False, unique=True)
    dc_id = Column(SmallInteger, nullable=False)

    is_banned = Column(Boolean, default=False, nullable=False)
