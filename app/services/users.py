from app.schemas.users import UserRegister, UserRegisterByAdmin, UserCreate, UserFromDB, UserUpdate, UserQueryParams
from app.exceptions.users import UserNotFound, UserEmailAlreadyExists, UserNoUpdateData
from app.repos.abstract.abstract_user_repo import AbstractUserRepository
from app.repos.abstract.abstract_role_repo import AbstractRoleRepo
from app.utils.passwords import get_password_hash, verify_password


class UserService:
    def __init__(self, user_repo: AbstractUserRepository, role_repo: AbstractRoleRepo) -> None:
        self.user_repo = user_repo
        self.role_repo = role_repo

    async def create_new_user(self, data: UserRegister|UserRegisterByAdmin) -> UserFromDB:
        user_data = data.model_dump()
        user_data['password_hash'] = get_password_hash(user_data['password'])
        role_names = user_data.pop('roles', None)
        try:
            user = await self.user_repo.create(UserCreate(**user_data))
        except UserEmailAlreadyExists:
            raise

        if role_names:
            await self._assign_roles_by_names(user.id, role_names)
        else:
            await self._assign_default_role(user.id)
        
        return await self.user_repo.get_by_id_with_roles(user.id)
    
    async def _assign_roles_by_names(self, user_id: int, role_names: list[str]):
        for role_name in role_names:
            role = await self.role_repo.get_by_name(role_name)
            if role:
                await self.role_repo.assign_role(user_id, role.id)

    async def _assign_default_role(self, user_id: int):
        default_role = await self.role_repo.get_by_name('customer')
        if default_role:
            await self.role_repo.assign_role(user_id, default_role.id)

    async def get_user_by_id(self, user_id: int, with_roles: bool = True) -> UserFromDB:
        try:
            if with_roles:
                user = await self.user_repo.get_by_id_with_roles(user_id)
            else:
                user = await self.user_repo.get_by_id(user_id)
        except UserNotFound:
            raise
        return user
    
    async def get_user_by_email(self, email: str) -> UserFromDB:
        try:
            user = await self.user_repo.get_by_email(email)
        except UserNotFound:
            raise
        return user
    
    async def get_users_by_params(self, params: UserQueryParams) -> list[UserFromDB]:
        query = params.model_dump(exclude=['limit', 'skip'], exclude_none=True)
        return await self.user_repo.get_by_params(query, params.limit, params.skip)
    
    async def count_users(self) -> int:
        return await self.user_repo.count()
    
    async def update_user(self, user_id: int, data: UserUpdate):
        try:
            return await self.user_repo.update_user(user_id, data)
        except (UserNotFound, UserNoUpdateData):
            raise
        
    async def delete_user(self, user_id) -> bool:
        try:
            return await self.user_repo.delete(user_id)
        except UserNotFound:
            raise

    async def change_password(self, user_id: int, new_password: str):
        new_password_hash = get_password_hash(new_password)
        try:
            await self.user_repo.update_password(user_id, new_password_hash)
        except UserNotFound:
            raise
    
    # def has_permission(self, permission_name: str) -> bool:
    #     '''
    #     Проверка наличия разрешения у пользователя.
    #     ВНИМАНИЕ: требует предварительной загрузки ролей и разрешений!
    #     '''
    #     # Оптимизированная проверка через set для производительности
    #     permissions = {
    #         permission.name 
    #         for role in self.roles 
    #         for permission in role.permissions
    #     }
    #     return permission_name in permissions
    
    # def has_permissions(self, *permission_names: str, require_all: bool = True) -> bool:
    #     '''
    #     Проверка нескольких разрешений.
    #     require_all=True: нужны все разрешения
    #     require_all=False: достаточно одного
    #     '''
    #     permissions = {
    #         permission.name 
    #         for role in self.roles 
    #         for permission in role.permissions
    #     }
        
    #     if require_all:
    #         return all(p in permissions for p in permission_names)
    #     else:
    #         return any(p in permissions for p in permission_names)
    
    # def has_role(self, role_name: str) -> bool:
    #     '''Проверка наличия роли'''
    #     return any(role.name == role_name for role in self.roles)
    
    # def has_any_role(self, *role_names: str) -> bool:
    #     '''Проверка наличия любой из указанных ролей'''
    #     roles = {role.name for role in self.roles}
    #     return any(role_name in roles for role_name in role_names)
    
    # def get_permissions(self) -> set:
    #     '''Получить все разрешения пользователя в виде set'''
    #     return {
    #         permission.name 
    #         for role in self.roles 
    #         for permission in role.permissions
    #     }