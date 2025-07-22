class CategoryException(Exception):
    pass


class CategoryNotFound(CategoryException):
    pass

class CreateCategoryException(CategoryException):
    pass

class UpdateCategoryException(CategoryException):
    pass


