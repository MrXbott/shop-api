from fastapi import status


class ProductException(Exception):
    def __init__(self, message: str, status_code: status):
        self.message = message or self.__class__.__name__
        self.status_code = status_code
        super().__init__(message)

class ProductNotFound(ProductException):
    def __init__(self, message='Product not found'):
        super().__init__(message, status.HTTP_404_NOT_FOUND)

class CreateProductException(ProductException):
    def __init__(self, message: str = 'Failed to create product'):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateProductException(ProductException):
    def __init__(self, message: str = 'Failed to update product'):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProductNoUpdateData(ProductException):
    def __init__(self, message: str = 'No data to update the product. At least one field must be provided for update.'):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


