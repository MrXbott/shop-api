from abc import ABC, abstractmethod

from app.schemas.categories import CategoryCreate
from app.models.categories import CategoryModel


class AbstractCategoryRepository(ABC):
    @abstractmethod
    async def create(self, data: CategoryCreate) -> CategoryModel:
        pass

    @abstractmethod
    async def delete(self, category_id: int) -> bool:
        pass