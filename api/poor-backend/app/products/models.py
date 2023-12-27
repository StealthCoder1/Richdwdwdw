from sqlalchemy import ARRAY, Column, Enum, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB

from app.database import Base
from app.products.constants import ProductType


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text)
    images = Column(ARRAY(Text))
    price = Column(Integer, nullable=False)
    type = Column(Enum(ProductType), nullable=False)
    payload = Column(JSONB, nullable=False)
