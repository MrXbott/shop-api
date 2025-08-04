from sqlalchemy import BigInteger, ForeignKey, Numeric, CheckConstraint, String, Float, Text, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column, validates
from sqlalchemy.dialects.postgresql import ARRAY

from typing import TYPE_CHECKING, Optional

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.categories import CategoryModel


class ProductModel(Base):
    __tablename__ = 'products'
    __table_args__ = (
        CheckConstraint('price > 0', name='check_price_positive'),
        CheckConstraint('rating >= 0 AND rating <= 5', name='check_rating_range'),
        CheckConstraint('quantity_in_stock >= 0', name='check_quantity_non_negative'),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    manufacturer: Mapped[str] = mapped_column(String, nullable=True)
    rating: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    quantity_in_stock: Mapped[int] = mapped_column(Integer, nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True, default=list)

    category: Mapped[Optional['CategoryModel']] = relationship(back_populates='products')