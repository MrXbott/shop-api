from sqlalchemy import BigInteger, ForeignKey, DateTime, Numeric, Enum as PgEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column, validates
from datetime import datetime
from typing import TYPE_CHECKING

from app.models.base import Base
from app.schemas.orders import OrderStatus

if TYPE_CHECKING:
    from app.models.users import UserModel
    from app.models.products import ProductModel


class OrderModel(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True) 

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    status: Mapped[OrderStatus] = mapped_column(PgEnum(OrderStatus, name='order_status'), default=OrderStatus.CREATED)
    total_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user: Mapped['UserModel'] = relationship(back_populates='orders')

    items: Mapped[list['OrderItemModel']] = relationship(back_populates='order', cascade='all, delete-orphan')


    
class OrderItemModel(Base):
    __tablename__ = 'order_items'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id', ondelete='CASCADE'), nullable=False)

    quantity: Mapped[int] = mapped_column(BigInteger, nullable=False)
    price_at_purchase: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    order: Mapped['OrderModel'] = relationship(back_populates='items')
    product: Mapped['ProductModel'] = relationship()