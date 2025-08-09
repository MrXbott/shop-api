from abc import ABC, abstractmethod

from app.schemas.categories import CategoryCreate, CategoryFromDB, CategoryUpdate
from app.models.categories import CategoryModel


class AbstractCategoryRepository(ABC):
    @abstractmethod
    async def create(self, data: CategoryCreate) -> CategoryFromDB:
        pass

    @abstractmethod
    async def get_by_id(self, category_id: int) -> CategoryFromDB: 
        pass

    @abstractmethod
    async def get_all(self) -> list[CategoryFromDB]: 
        pass

    @abstractmethod
    async def count(self) -> int:
        pass

    @abstractmethod
    async def update(self, category_id: int, data: CategoryUpdate) -> CategoryFromDB:
        pass

    @abstractmethod
    async def delete(self, category_id: int) -> bool:
        pass