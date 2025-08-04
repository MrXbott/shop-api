from sqlalchemy import update, select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.repos.abstract.abstract_category_repo import AbstractCategoryRepository
from app.models.categories import CategoryModel
from app.schemas.categories import CategoryCreate


class CategoryPostgresRepo(AbstractCategoryRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: CategoryCreate) -> CategoryModel:
        category_data = data.model_dump()
        category = CategoryModel(**category_data)
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return category

    async def delete(self, category_id: int) -> bool:
        result = await self.session.execute(delete(CategoryModel).where(CategoryModel.id == category_id))
        await self.session.commit()
        return result.rowcount > 0