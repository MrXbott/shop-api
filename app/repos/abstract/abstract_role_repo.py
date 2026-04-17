from abc import ABC, abstractmethod

from app.schemas.roles import RoleFromDB, RoleCreate

class AbstractRoleRepo(ABC):
    @abstractmethod
    async def create(self, data: RoleCreate) -> RoleFromDB:
        pass

    @abstractmethod
    async def get_by_id(self, role_id: int) -> RoleFromDB:
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> RoleFromDB:
        pass

    @abstractmethod
    async def assign_role(self, user_id: int, role_id: int) -> RoleFromDB:
        pass
        