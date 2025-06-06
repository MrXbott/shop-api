from fastapi import HTTPException
from bson import ObjectId
from datetime import datetime

from app.schemas.orders import OrderItem, OrderBase, OrderCreate, OrderStatus, OrderFromDB, OrderUpdate, OrderQueryParams
from app.db.crud.orders import OrderCRUD
from app.services.products import Product
from app.services.base import BaseService
from app.exceptions.orders import OrderNotFound, InvalidStatusTransition, NotEnoughStock
from app.exceptions.users import InvalidUserIdFormat

ALLOWED_STATUS_TRANSITIONS = {
    OrderStatus.CREATED: {
        OrderStatus.WAITING_FOR_PAYMENT, 
        OrderStatus.CANCELLED
        },
    OrderStatus.WAITING_FOR_PAYMENT: {
        OrderStatus.PAID, 
        OrderStatus.CANCELLED
        },
    OrderStatus.PAID: {
        OrderStatus.SHIPPED, 
        OrderStatus.CANCELLED
        },
    OrderStatus.SHIPPED: {
        OrderStatus.COMPLETED
        },
    OrderStatus.COMPLETED: set(),
    OrderStatus.CANCELLED: set(),
}

class Order(BaseService[OrderCreate, OrderFromDB, OrderUpdate, OrderQueryParams]):
    crud_class = OrderCRUD
    return_schema_class = OrderFromDB

    @staticmethod
    def _is_valid_status_transition(current_status: str, new_status: str) -> bool:
        return new_status in ALLOWED_STATUS_TRANSITIONS.get(current_status, set())

    @staticmethod
    def _calculate_total_price(items: list[OrderItem]) -> float:
        return sum(item.quantity * item.price_at_purchase for item in items)

    @classmethod
    async def create(cls, order: OrderBase) -> OrderFromDB:
        order_data = order.model_dump(by_alias=True)

        updated_products = []
        for item in order_data['items']:
            product = await Product.reserve(item['product_id'], item['quantity'])
            if not product:
                for rollback_item in updated_products:
                    await Product.reverse_reserve(rollback_item['product_id'], rollback_item['quantity'])
                raise NotEnoughStock(f'Not enough stock for product {item['product_id']}')
            updated_products.append(item)

        total_price = Order._calculate_total_price(order.items)
        order_data.update({
            'total_price': total_price,
            'status': OrderStatus.CREATED,
            'created_at': datetime.now()
        })        
            
        return await super().create(OrderCreate(**order_data))

    @staticmethod
    async def update_status(order_id: str, new_status: OrderStatus) -> OrderFromDB:
        order = await OrderCRUD.get_by_id(order_id)
        if not order:
            raise OrderNotFound('Order not found')
        current_status = order['status']
        if not Order._is_valid_status_transition(current_status, new_status):
            raise InvalidStatusTransition(f'Invalid status transition: {current_status} → {new_status.value}')
        
        result = await OrderCRUD.update_status(order_id, new_status)
        if result.matched_count == 0:
            raise OrderNotFound('Order not found')
        
        updated_order = await Order._get_object_or_404(order_id)
        return OrderFromDB(**updated_order)
    
    @classmethod
    async def get_by_params(cls, params: OrderQueryParams) -> list[OrderFromDB]:
        if params.user_id:
            try:
                ObjectId(params.user_id)
            except Exception:
                raise InvalidUserIdFormat('Invalid user_id format')
        return await super().get_by_params(params)

