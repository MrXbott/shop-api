from sqlalchemy import update, select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.repos.abstract.abstract_product_repo import AbstractProductRepository
from app.models.products import ProductModel
from app.schemas.products import ProductCreate, ProductUpdate, ProductFromDB
from app.exceptions.products import ProductNotFound, ProductNoUpdateData


class ProductRepoPostgres(AbstractProductRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: ProductCreate) -> ProductFromDB:
        product_data = data.model_dump()
        product = ProductModel(**product_data)
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return ProductFromDB.model_validate(product)

    async def get_by_id(self, product_id: int) -> ProductFromDB: 
        result = await self.session.execute(
            select(ProductModel)
            .where(ProductModel.id == product_id)
            )
        product = result.scalar_one_or_none()
        if not product:
            raise ProductNotFound()
        return ProductFromDB.model_validate(product)
    

    async def get_by_params(self, params: dict, limit: int = 100, skip: int = 0) -> list[ProductFromDB]:
        stmt = select(ProductModel)

        for key, value in params.items():
            if hasattr(ProductModel, key):
                stmt = stmt.where(getattr(ProductModel, key) == value)

        stmt = stmt.limit(limit).offset(skip).order_by(ProductModel.id)

        result = await self.session.execute(stmt)
        products = result.scalars().all()

        return [ProductFromDB.model_validate(product) for product in products]
    
    
    async def count(self) -> int:
        result = await self.session.execute(select(func.count(ProductModel.id)))
        return result.scalar_one()
    

    async def update_product(self, product_id: int, data: ProductUpdate) -> ProductFromDB:
        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            return ProductNoUpdateData()

        result = await self.session.execute(
            update(ProductModel)
            .where(ProductModel.id == product_id)
            .values(**update_data)
            .returning(ProductModel)
        )
        updated_product = result.scalar_one_or_none()

        if updated_product is None:
            raise ProductNotFound()
        
        await self.session.commit()
        return ProductFromDB.model_validate(updated_product)
    
    # async def set_quantity_in_stock(self, product_id: int, quantity: int) -> ProductFromDB:
    #     result = await self.session.execute(
    #         update(ProductModel)
    #         .where(ProductModel.id == product_id)
    #         .values(quantity_in_stock=quantity)
    #         .returning(ProductModel)
    #     )
    #     updated_product = result.scalar_one_or_none()

    #     if updated_product is None:
    #         raise ProductNotFound()
        
    #     await self.session.commit()
    #     return ProductFromDB.model_validate(updated_product)
    
    async def delete(self, product_id: int) -> bool:
        result = await self.session.execute(
            delete(ProductModel)
            .where(ProductModel.id == product_id)
            )
        await self.session.commit()

        if result.rowcount == 0:
            raise ProductNotFound()
        
        return True