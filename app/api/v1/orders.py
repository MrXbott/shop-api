from fastapi import APIRouter, HTTPException, status, Depends

from app.schemas.orders import OrderBase, OrderFromDB, OrderQueryParams, StatusUpdate
from app.services.orders import Order
from app.auth.dependencies import get_admin_user, get_current_user

router = APIRouter(prefix='/orders')

@router.post('/', response_model=OrderFromDB, response_model_by_alias=False, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_admin_user)])
async def create_order(order: OrderBase):
    return await Order.create(order)

@router.get('/', response_model=list[OrderFromDB], response_model_by_alias=False, status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def get_orders(params: OrderQueryParams = Depends()):
    return await Order.get_by_params(params)

@router.get('/count', status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def get_orders_count():    
    return {'orders_count': await Order.count()}

@router.get('/{order_id}', response_model=OrderFromDB, response_model_by_alias=False, status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def get_order_by_id(order_id: str):
    return await Order.get_by_id(order_id)

@router.patch('/{order_id}/status', response_model=OrderFromDB, response_model_by_alias=False, status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def update_order_status(order_id: str, status_body: StatusUpdate):
    updated_order = await Order.update_status(order_id, status_body.status)
    return updated_order

@router.delete('/{order_id}', status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def delete_order_by_id(order_id: str):
    await Order.delete(order_id)
    return {'message': 'Order deleted'}



