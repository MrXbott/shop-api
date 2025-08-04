from sqlalchemy import BigInteger, String
from sqlalchemy.orm import relationship, Mapped, mapped_column, validates

from typing import TYPE_CHECKING

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.products import ProductModel


class CategoryModel(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    products: Mapped[list['ProductModel']] = relationship(back_populates='category', cascade='all, delete-orphan', passive_deletes=True)