from fastapi import status

from app.schemas.orders import OrderStatus

class OrderException(Exception):
    def __init__(self, message: str, status_code: status):
        self.message = message or self.__class__.__name__
        self.status_code = status_code
        super().__init__(message)


class OrderNotFound(OrderException):
    def __init__(self, message='Order not found.'):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class InvalidStatusTransition(OrderException):
    def __init__(self, current_status: OrderStatus, new_status: OrderStatus, message='Invalid status transition.'):
        self.message = f'{message} {current_status} -> {new_status}'
        super().__init__(self.message, status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotEnoughStock(OrderException):
    """Not enough items in stock.."""
    pass



