class OrderException(Exception):
    """Basic exception for orders."""
    pass


class OrderNotFound(OrderException):
    """Order not found."""
    pass


class InvalidStatusTransition(OrderException):
    """Invalid order status transition."""
    pass


class NotEnoughStock(OrderException):
    """Not enough items in stock.."""
    pass


class InvalidUserIdFormat(OrderException):
    """Invalid user_id format."""
    pass
