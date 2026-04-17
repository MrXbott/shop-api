# app/repositories/role_repository.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from typing import Optional, List

from app.repos.abstract.abstract_role_repo import AbstractRoleRepo
from app.schemas.roles import RoleCreate, RoleFromDB
from app.models.roles import RoleModel, PermissionModel
from app.models.users import UserModel
from app.exceptions.roles import RoleNotFound
from app.exceptions.users import UserNotFound

class RoleRepoPostgres(AbstractRoleRepo):    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: RoleCreate) -> RoleFromDB:
        role_data = data.model_dump()
        role = RoleModel(**role_data)
        try:
            self.session.add(role)
            await self.session.commit()
            await self.session.refresh(role)
            return RoleFromDB.model_validate(role)
        except IntegrityError:
            await self.session.rollback()

    
    async def get_by_id(self, role_id: int) -> RoleFromDB:
        result = await self.session.execute(
            select(RoleModel)
            .where(RoleModel.id == role_id)
            .options(
                selectinload(RoleModel.permissions)
            )
        )
        role = result.scalar_one_or_none()

        if not role:
            raise RoleNotFound()
        return RoleFromDB.model_validate(role)
    
    
    async def get_by_name(self, name: str) -> RoleFromDB:
        result = await self.session.execute(
            select(RoleModel)
            .where(RoleModel.name == name)
            .options(
                selectinload(RoleModel.permissions)
            )
        )
        role = result.scalar_one_or_none()

        if not role:
            raise RoleNotFound()
        return RoleFromDB.model_validate(role)
    
    async def assign_role(self, user_id: int, role_id: int) -> RoleFromDB:
        result = await self.session.execute(
            select(UserModel)
            .where(UserModel.id == user_id)
            .options(
                selectinload(UserModel.roles)
            )
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise UserNotFound()
        
        role = await self.session.get(RoleModel, role_id)
        if not role:
            raise RoleNotFound()
        
        if role not in user.roles:
            user.roles.append(role)
            await self.session.commit()
        
        return RoleFromDB.model_validate(role)
    
    