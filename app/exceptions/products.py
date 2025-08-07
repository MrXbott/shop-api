class ProductException(Exception):
    pass


class ProductNotFound(ProductException):
    pass

class CreateProductException(ProductException):
    pass

class UpdateProductException(ProductException):
    pass

class ProductNoUpdateData(ProductException):
    pass


