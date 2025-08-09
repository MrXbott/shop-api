from fastapi import APIRouter, HTTPException, status, Depends

from app.schemas.orders import OrderBase, OrderFromDB, OrderQueryParams, StatusUpdate
from app.services.orders import OrderService
from app.exceptions.orders import OrderNotFound, InvalidStatusTransition, NotEnoughStock
from app.exceptions.users import InvalidUserIdFormat
from app.dependencies.services import get_order_service
from app.dependencies.users import get_admin_user, get_current_user

router = APIRouter(prefix='/orders')

@router.post('/', response_model=OrderFromDB, response_model_by_alias=False, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_admin_user)])
async def create_order(order_data: OrderBase, service: OrderService = Depends(get_order_service)):
    try:
        return await service.add_new_order(order_data)
    except (NotEnoughStock, InvalidStatusTransition) as e:
        raise HTTPException(e.status_code, e.message)

@router.get('/', response_model=list[OrderFromDB], response_model_by_alias=False, status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def get_orders(params: OrderQueryParams = Depends(), service: OrderService = Depends(get_order_service)):
    return await service.get_orders_by_params(params)

@router.get('/count', status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def get_orders_count(service: OrderService = Depends(get_order_service)):    
    return {'orders_count': await service.count_orders()}

@router.get('/{order_id}', response_model=OrderFromDB, response_model_by_alias=False, status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def get_order_by_id(order_id: int, service: OrderService = Depends(get_order_service)):
    try:
        return await service.get_order_by_id(order_id)
    except OrderNotFound as e:
        raise HTTPException(e.status_code, e.message)

@router.patch('/{order_id}/status', response_model=OrderFromDB, response_model_by_alias=False, status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def update_order_status(order_id: str, status_body: StatusUpdate, service: OrderService = Depends(get_order_service)):
    try:
        return await service.update_order_status(order_id, status_body.status)
    except (InvalidStatusTransition, OrderNotFound) as e:
        raise HTTPException(e.status_code, e.message)





