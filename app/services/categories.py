from app.repos.mongo.categories import CategoryCRUD
from app.schemas.categories import CategoryCreate, CategoryFromDB, CategoryUpdate, CategoryQueryParams
from app.services.base import BaseService
from app.exceptions.categories import CategoryNotFound, CreateCategoryException, UpdateCategoryException

class Category(BaseService[CategoryCreate, CategoryFromDB, CategoryUpdate, CategoryQueryParams]):
    crud_class = CategoryCRUD
    return_schema_class = CategoryFromDB

    not_found_exception = CategoryNotFound
    creation_failed_exception = CreateCategoryException
    update_failed_exception = UpdateCategoryException
