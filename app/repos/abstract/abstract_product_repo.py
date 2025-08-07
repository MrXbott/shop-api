from abc import ABC, abstractmethod

from app.models.products import ProductModel
from app.schemas.products import ProductCreate, ProductUpdate, ProductFromDB


class AbstractProductRepository(ABC):

    @abstractmethod
    async def create(self, data: ProductCreate) -> ProductFromDB:
        pass

    @abstractmethod
    async def get_by_id(self, product_id: int) -> ProductFromDB: 
        pass

    @abstractmethod
    async def count(self) -> int:
        pass

    @abstractmethod
    async def get_by_params(self, params: dict, limit: int = 100, offset: int = 0) -> list[ProductFromDB]:
        pass
    
    @abstractmethod
    async def update_product(self, product_id: int, data: ProductUpdate) -> ProductFromDB:
        pass

    # @abstractmethod
    # async def set_quantity_in_stock(self, product_id: int, quantity: int) -> ProductFromDB:
    #     pass

    @abstractmethod
    async def delete(self, product_id: int) -> bool:
        pass

    