from fastapi import APIRouter, HTTPException, status, Depends

from app.schemas.orders import OrderBase, OrderFromDB, OrderQueryParams, StatusUpdate
from app.services.orders import Order
from app.auth.dependencies import get_admin_user, get_current_user
from app.exceptions.orders import OrderNotFound, InvalidStatusTransition, NotEnoughStock
from app.exceptions.users import InvalidUserIdFormat

router = APIRouter(prefix='/orders')

@router.post('/', response_model=OrderFromDB, response_model_by_alias=False, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_admin_user)])
async def create_order(order: OrderBase):
    try:
        return await Order.create(order)
    except NotEnoughStock as e:
        raise HTTPException(400, str(e))
    except InvalidUserIdFormat as e:
        raise HTTPException(400, str(e))

@router.get('/', response_model=list[OrderFromDB], response_model_by_alias=False, status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def get_orders(params: OrderQueryParams = Depends()):
    try:
        return await Order.get_by_params(params)
    except InvalidUserIdFormat as e:
        raise HTTPException(400, str(e))

@router.get('/count', status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def get_orders_count():    
    return {'orders_count': await Order.count()}

@router.get('/{order_id}', response_model=OrderFromDB, response_model_by_alias=False, status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def get_order_by_id(order_id: str):
    return await Order.get_by_id(order_id)

@router.patch('/{order_id}/status', response_model=OrderFromDB, response_model_by_alias=False, status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def update_order_status(order_id: str, status_body: StatusUpdate):
    try:
        return await Order.update_status(order_id, status_body.status)
    except InvalidStatusTransition as e:
        raise HTTPException(400, str(e))
    except OrderNotFound as e:
        raise HTTPException(404, str(e))

@router.delete('/{order_id}', status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def delete_order_by_id(order_id: str):
    await Order.delete(order_id)
    return {'message': 'Order deleted'}



