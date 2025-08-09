from app.repos.mongo.categories import CategoryRepoMongo
from app.schemas.categories import CategoryCreate, CategoryFromDB, CategoryUpdate, CategoryQueryParams
from app.services.base import BaseService
from app.exceptions.categories import CategoryNotFound, CreateCategoryException, UpdateCategoryException, CategoryNoUpdateData
from app.repos.abstract.abstract_category_repo import AbstractCategoryRepository

class CategoryService:
    def __init__(self, repo: AbstractCategoryRepository) -> None:
        self.repo = repo

    async def add_new_category(self, data: CategoryCreate) -> CategoryFromDB:
        return await self.repo.create(data)
    
    async def get_category_by_id(self, category_id: int) -> CategoryFromDB:
        try:
            return await self.repo.get_by_id(category_id)
        except CategoryNotFound:
            raise
    
    async def get_all_categories(self) -> list[CategoryFromDB]:
        return await self.repo.get_all()
    
    async def count_categories(self) -> int:
        return await self.repo.count()
    
    async def update_category(self, category_id: int,  data: CategoryUpdate):
        try:
            return await self.repo.update(category_id, data)
        except (CategoryNotFound, CategoryNoUpdateData):
            raise

    async def delete_category(self, category_id: int) -> bool:
        try:
            return await self.repo.delete(category_id)
        except CategoryNotFound:
            raise