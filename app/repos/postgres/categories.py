from sqlalchemy import update, select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.repos.abstract.abstract_category_repo import AbstractCategoryRepository
from app.models.categories import CategoryModel
from app.schemas.categories import CategoryCreate, CategoryFromDB, CategoryUpdate
from app.exceptions.categories import CategoryNotFound, CategoryNoUpdateData


class CategoryRepoPostgres(AbstractCategoryRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: CategoryCreate) -> CategoryFromDB:
        category_data = data.model_dump()
        category = CategoryModel(**category_data)
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return CategoryFromDB.model_validate(category)
    
    async def get_by_id(self, category_id: int) -> CategoryFromDB:
        result = await self.session.execute(
            select(CategoryModel)
            .where(CategoryModel.id == category_id)
        )
        category = result.scalar_one_or_none()
        if not category:
            raise CategoryNotFound()
        return CategoryFromDB.model_validate(category)
    
    async def get_all(self) -> list[CategoryFromDB]:
        result = await self.session.execute(
            select(CategoryModel)
        )
        categories = result.scalars().all()
        return [CategoryFromDB.model_validate(category) for category in categories]
    
    async def count(self) -> int:
        result = await self.session.execute(
            select(func.count(CategoryModel.id))
            )
        return result.scalar_one()

    async def update(self, category_id: int, data: CategoryUpdate) -> CategoryFromDB:
        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            raise CategoryNoUpdateData()

        result = await self.session.execute(
            update(CategoryModel)
            .where(CategoryModel.id == category_id)
            .values(**update_data)
            .returning(CategoryModel)
        )
        updated_category = result.scalar_one_or_none()

        if updated_category is None:
            raise CategoryNotFound()
        
        await self.session.commit()
        return CategoryFromDB.model_validate(updated_category)

    async def delete(self, category_id: int) -> bool:
        result = await self.session.execute(
            delete(CategoryModel)
            .where(CategoryModel.id == category_id)
            )
        await self.session.commit()

        if result.rowcount == 0:
            raise CategoryNotFound()
        
        return True
    