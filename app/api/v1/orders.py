from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId
from typing import List, Optional
from datetime import datetime

from app.db.database import db
from app.models.orders import OrderCreate, OrderFromDB, OrderItem, OrderStatus, StatusUpdate

router = APIRouter(prefix='/orders')

ALLOWED_STATUS_TRANSITIONS = {
    'created': {'waiting_for_payment', 'cancelled'},
    'waiting_for_payment': {'paid', 'cancelled'},
    'paid': {'shipped', 'cancelled'},
    'shipped': {'completed'},
    'completed': set(),
    'cancelled': set(),
}

def is_valid_status_transition(current_status: str, new_status: str) -> bool:
    return new_status in ALLOWED_STATUS_TRANSITIONS.get(current_status, set())

@router.post('/', response_model=OrderFromDB)
async def create_order(order: OrderCreate):
    items: List[OrderItem] = order.items
    total_price = sum(item.quantity * item.price_at_purchase for item in items)

    order_data = order.model_dump(by_alias=True)
    order_data['total_price'] = total_price
    order_data['status'] = OrderStatus.CREATED
    order_data['created_at'] = datetime.now()
    
    result = await db.get_collection('orders').insert_one(order_data)
    new_order = await db.get_collection('orders').find_one({'_id': result.inserted_id})
    if not new_order:
        raise HTTPException(500, 'Failed to fetch inserted product')
    return new_order

@router.get('/', response_model=List[OrderFromDB], response_model_by_alias=False)
async def get_orders(
                user_id: Optional[str] = Query(None), 
                status: Optional[OrderStatus] = Query(None),
                limit: int = Query(100, ge=1, le=100),
                skip: int = Query(0, ge=0),
                ):
    query = {}
    if user_id:
            ObjectId(user_id) # just to check if user_id is valid format
            query['user_id'] = user_id
    if status:
        query['status'] = status.value
    orders = await db.get_collection('orders').find(query).skip(skip).limit(limit).to_list(length=limit)
    return orders

@router.get('/count')
async def get_orders_count():
    count = await db.get_collection('orders').count_documents({})
    return {'orders_count': count}

@router.get('/{id}', response_model=OrderFromDB, response_model_by_alias=False)
async def get_order_by_id(id: str):
    order = await db.get_collection('orders').find_one({'_id': ObjectId(id)})
    if not order:
        raise HTTPException(404, 'Order not found')
    return order

@router.patch('/{id}/status', response_model=OrderFromDB, response_model_by_alias=False)
async def update_order_status(id: str, status_body: StatusUpdate):
    obj_id = ObjectId(id)
    new_status = status_body.status
    order = await db.get_collection('orders').find_one({'_id': obj_id})
    if not order:
        raise HTTPException(404, 'Order not found')
    current_status = order['status']
    if not is_valid_status_transition(current_status, new_status):
        raise HTTPException(400, f'Invalid status transition: {current_status} → {new_status}')
    
    result = await db.get_collection('orders').update_one({'_id': obj_id}, {'$set': {'status': new_status, 'updated_at': datetime.now()}})
    if result.matched_count == 0:
        raise HTTPException(404, 'Order not found')
    
    updated_order = await db.get_collection('orders').find_one({'_id': obj_id})
    if not updated_order:
        raise HTTPException(500, 'Failed to fetch inserted product')
    return updated_order

@router.delete('/{id}')
async def delete_order_by_id(id: str):
    result = await db.get_collection('orders').delete_one(({'_id': ObjectId(id)}))
    if result.deleted_count == 0:
        raise HTTPException(404, detail='Order not found')
    return {'message': 'Order deleted'}



