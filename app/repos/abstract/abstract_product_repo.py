from abc import ABC, abstractmethod

from app.models.products import ProductModel
from app.schemas.products import ProductCreate, ProductUpdate


class AbstractProductRepository(ABC):

    @abstractmethod
    async def create(self, data: ProductCreate) -> ProductModel:
        pass

    @abstractmethod
    async def get_by_id(self, product_id: int) -> ProductModel: 
        pass

    @abstractmethod
    async def count(self) -> int:
        pass

    @abstractmethod
    async def get_all(self) -> list[ProductModel]:
        pass

    @abstractmethod
    async def get_by_params(self, params: dict, limit: int = 100, offset: int = 0) -> list[ProductModel]:
        pass
    
    @abstractmethod
    async def update_info(self, product_id: int, data: ProductUpdate) -> bool:
        pass

    @abstractmethod
    async def set_quantity_in_stock(self, product_id: int, quantity: int) -> bool:
        pass

    @abstractmethod
    async def delete(self, product_id: int) -> bool:
        pass

    