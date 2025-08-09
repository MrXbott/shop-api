from pymongo.collection import Collection

from app.repos.abstract.abstract_category_repo import AbstractCategoryRepository
from app.schemas.categories import CategoryCreate, CategoryFromDB, CategoryUpdate, CategoryQueryParams


class CategoryRepoMongo(AbstractCategoryRepository):
    def __init__(self, collection: Collection):
        self.collection = collection

    async def create(self, data: CategoryCreate) -> CategoryFromDB:
        pass

    async def get_by_id(self, category_id: int) -> CategoryFromDB: 
        pass

    async def get_all(self) -> list[CategoryFromDB]: 
        pass

    async def count(self) -> int:
        pass

    async def update(self, category_id: int, data: CategoryUpdate) -> CategoryFromDB:
        pass

    async def delete(self, category_id: int) -> bool:
        pass