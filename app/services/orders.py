from fastapi import HTTPException
from bson import ObjectId
from datetime import datetime
from app.schemas.orders import OrderItem, OrderCreate, OrderStatus, OrderFromDB, OrderQueryParams
from app.db.crud.orders import OrderCRUD

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

class Order:
    @staticmethod
    async def _get_order_or_404(order_id: str) -> dict:
        order = await OrderCRUD.get_by_id(order_id)
        if not order:
            raise HTTPException(404, 'Order not found')
        return order

    @staticmethod
    def _is_valid_status_transition(current_status: str, new_status: str) -> bool:
        return new_status in ALLOWED_STATUS_TRANSITIONS.get(current_status, set())

    @staticmethod
    def _calculate_total_price(items: list[OrderItem]) -> float:
        return sum(item.quantity * item.price_at_purchase for item in items)

    @staticmethod
    async def create(order: OrderCreate) -> OrderFromDB:
        total_price = Order._calculate_total_price(order.items)
        order_data = order.model_dump(by_alias=True)
        order_data.update({
            'total_price': total_price,
            'status': OrderStatus.CREATED,
            'created_at': datetime.now()
        })
        result = await OrderCRUD.create(order_data)
        if not result.inserted_id:
            raise HTTPException(500, 'Failed to insert new order')
        
        new_order = await Order._get_order_or_404(result.inserted_id)
        return OrderFromDB(**new_order)

    @staticmethod
    async def update_status(order_id: str, new_status: str) -> OrderFromDB:
        order = await OrderCRUD.get_by_id(order_id)
        if not order:
            raise HTTPException(404, 'Order not found')
        current_status = order['status']
        if not Order._is_valid_status_transition(current_status, new_status):
            raise HTTPException(400, f'Invalid status transition: {current_status} → {new_status}')
        
        result = await OrderCRUD.update_status(order_id, new_status)
        if result.matched_count == 0:
            raise HTTPException(404, 'Order not found')
        
        updated_order = await Order._get_order_or_404(order_id)
        return OrderFromDB(**updated_order)
    
    @staticmethod
    async def count() -> int:
        return await OrderCRUD.get_count()

    @staticmethod
    async def get_by_id(order_id: str) -> OrderFromDB:
        order = await OrderCRUD.get_by_id(order_id)
        if not order:
            raise HTTPException(404, 'Order not found')
        return OrderFromDB(**order)
    
    @staticmethod
    async def get_orders(params: OrderQueryParams) -> list[OrderFromDB]:
        query = {}
        if params.user_id:
            try:
                ObjectId(params.user_id)
            except Exception:
                raise HTTPException(400, detail='Invalid user_id format')
            query['user_id'] = params.user_id
        if params.status:
            query['status'] = params.status.value
        orders = await OrderCRUD.get(query, params.limit, params.skip)
        return [OrderFromDB(**order) for order in orders]
    
    @staticmethod
    async def delete(order_id: str) -> None:
        result = await OrderCRUD.delete_by_id(order_id)
        if result.deleted_count == 0:
            raise HTTPException(404, detail='Order not found')
