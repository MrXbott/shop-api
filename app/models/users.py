from sqlalchemy import BigInteger, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import TYPE_CHECKING

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.orders import OrderModel, OrderItemModel

class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True) 
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False, default='user')

    orders: Mapped[list['OrderModel']] = relationship(back_populates='user', cascade='all, delete-orphan')

