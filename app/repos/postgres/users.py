from sqlalchemy import delete, select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.repos.abstract.abstract_user_repo import AbstractUserRepository
from app.models.users import UserModel
from app.schemas.users import UserFromDB, UserCreate, UserUpdate

from app.exceptions.users import UserEmailAlreadyExists, UserNotFound, UserNoUpdateData


class UserRepoPostgres(AbstractUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: UserCreate) -> UserFromDB:
        user_data = data.model_dump()
        user = UserModel(**user_data)
        try:
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return UserFromDB.model_validate(user)
        except IntegrityError:
            await self.session.rollback()
            raise UserEmailAlreadyExists()

    async def get_by_id(self, user_id: int) -> UserFromDB:
        result = await self.session.execute(select(UserModel).where(UserModel.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFound()
        return UserFromDB.model_validate(user)

    async def get_by_email(self, email: str) -> UserFromDB: 
        # result = await self.session.execute(select(UserModel).where(UserModel.email == email))
        result = await self.session.execute(select(UserModel).where(func.lower(UserModel.email) == email.lower()))
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFound()
        return UserFromDB.model_validate(user)
    
    async def get_by_params(self, params: dict, limit: int = 100, skip: int = 0) -> list[UserFromDB]:
        stmt = select(UserModel)

        for key, value in params.items():
            if hasattr(UserModel, key):
                stmt = stmt.where(getattr(UserModel, key) == value)

        stmt = stmt.limit(limit).offset(skip).order_by(UserModel.id)

        result = await self.session.execute(stmt)
        users = result.scalars().all()
        return [UserFromDB.model_validate(user) for user in users]
    
    async def count(self) -> int:
        result = await self.session.execute(select(func.count(UserModel.id)))
        return result.scalar_one()
    
    async def update_user(self, user_id: int, data: UserUpdate) -> UserFromDB:
        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            raise UserNoUpdateData()
        
        result = await self.session.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(**update_data)
            .returning(UserModel)
        )
        updated_user = result.scalar_one_or_none()

        if updated_user is None:
            raise UserNotFound()
        
        await self.session.commit()

        return UserFromDB.model_validate(updated_user)
    
    async def update_password(self, user_id: int, new_password_hash: str) -> None:
        result = await self.session.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(password_hash=new_password_hash)
            .returning(UserModel.id)
        )
        await self.session.commit()

        updated_user = result.scalar_one_or_none()

        if updated_user is None:
            raise UserNotFound()


    async def delete(self, identifier: int|str) -> bool:
        if isinstance(identifier, str) and '@' in identifier:
            stmt = delete(UserModel).where(UserModel.email == identifier)
        else:
            stmt = delete(UserModel).where(UserModel.id == identifier)

        result = await self.session.execute(stmt)
        await self.session.commit()
        
        if result.rowcount == 0:
            raise UserNotFound()
        
        return True
