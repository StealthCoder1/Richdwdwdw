from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Enum,
    ForeignKey,
    Integer,
    LargeBinary,
    Text,
)

from app.database import Base
from app.products.constants import LicenseIds


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    email = Column(Text, index=True)
    username = Column(Text, index=True)
    password = Column(LargeBinary)
    balance = Column(Integer, nullable=False, default=0)
    is_email_confirmed = Column(Boolean, nullable=False, default=False)


class UserTelegram(Base):
    __tablename__ = "user_telegram"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    user_id = Column(
        Integer, ForeignKey("user.id"), index=True, unique=True, nullable=False
    )
    username = Column(Text, index=True)


class UserLicense(Base):
    __tablename__ = "user_license"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    license_id = Column(Enum(LicenseIds), nullable=False)
    expires_at = Column(Integer, nullable=False)
