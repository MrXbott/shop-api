from sqlalchemy import update, select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.repos.abstract.abstract_product_repo import AbstractProductRepository
from app.models.products import ProductModel
from app.schemas.products import ProductCreate, ProductUpdate


class ProductPostgresRepo(AbstractProductRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: ProductCreate) -> ProductModel:
        product_data = data.model_dump()
        product = ProductModel(**product_data)
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def get_by_id(self, product_id: int) -> ProductModel|None: 
        result = await self.session.execute(select(ProductModel).where(ProductModel.id == product_id))
        return result.scalar_one_or_none()

    async def get_all(self) -> list[ProductModel]:
        result = await self.session.execute(select(ProductModel))
        return result.scalars().all()
    
    async def get_by_params(self, params: dict, limit: int = 100, offset: int = 0) -> list[ProductModel]:
        stmt = select(ProductModel)

        for key, value in params.items():
            if hasattr(ProductModel, key):
                stmt = stmt.where(getattr(ProductModel, key) == value)

        stmt = stmt.limit(limit).offset(offset).order_by(ProductModel.name)

        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def count(self) -> int:
        result = await self.session.execute(select(func.count(ProductModel.id)))
        return result.scalar_one()
    
    async def update_info(self, product_id: int, data: ProductUpdate) -> bool:
        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            return False 

        result = await self.session.execute(
            update(ProductModel)
            .where(ProductModel.id == product_id)
            .values(**update_data)
            .returning(ProductModel.id)
        )
        updated_id = result.scalar()
        await self.session.commit()

        return updated_id is not None
    
    async def set_quantity_in_stock(self, product_id: int, quantity: int) -> bool:
        result = await self.session.execute(
            update(ProductModel)
            .where(ProductModel.id == product_id)
            .values(quantity_in_stock=quantity)
            .returning(ProductModel.id)
        )
        updated_id = result.scalar()
        await self.session.commit()
        return updated_id is not None
    
    async def delete(self, product_id: int) -> bool:
        result = await self.session.execute(delete(ProductModel).where(ProductModel.id == product_id))
        await self.session.commit()
        return result.rowcount > 0