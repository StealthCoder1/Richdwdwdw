from sqlalchemy import Column, DateTime, Integer, Text

from app.database import Base


class Proxy(Base):
    __tablename__ = "proxy"

    id = Column(Integer, primary_key=True)
    url = Column(Text, unique=True, index=True, nullable=False)
    latency = Column(Integer)
    last_checked_at = Column(DateTime)
