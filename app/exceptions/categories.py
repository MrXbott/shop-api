from fastapi import status

class CategoryException(Exception):
    def __init__(self, message: str, status_code: status):
        self.message = message or self.__class__.__name__
        self.status_code = status_code
        super().__init__(message)


class CategoryNotFound(CategoryException):
    def __init__(self, message: str = 'Category not found'):
        super().__init__(message, status.HTTP_404_NOT_FOUND)

class CreateCategoryException(CategoryException):
    def __init__(self, message: str = 'Failed to create category'):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateCategoryException(CategoryException):
    def __init__(self, message: str = 'Failed to update category'):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)

class CategoryNoUpdateData(CategoryException):
    def __init__(self, message: str = 'No data to update the category. At least one field must be provided for update.'):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


