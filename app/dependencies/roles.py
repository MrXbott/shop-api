from fastapi import Depends, HTTPException, status

from app.schemas.users import UserFromDB
from app.dependencies.users import get_current_user


class PermissionChecker:
    def __init__(
        self, 
        required_permissions: list[str],
        require_all: bool = True  
    ):
        self.required_permissions = required_permissions
        self.require_all = require_all
    
    async def __call__(
        self,
        current_user: UserFromDB = Depends(get_current_user),
    ):
        user_permissions = set()
        for role in current_user.roles:
            for perm in role.permissions:
                user_permissions.add(perm.name)
        
        if self.require_all:
            if not all(p in user_permissions for p in self.required_permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f'Missing permissions: {self.required_permissions}'
                )
        else:
            if not any(p in user_permissions for p in self.required_permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f'Need at least one of: {self.required_permissions}'
                )
        return current_user

class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles
    
    async def __call__(self, current_user: UserFromDB = Depends(get_current_user)):
        user_roles = [role.name for role in current_user.roles]
        if not all(r in user_roles for r in self.allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'Role required: {self.allowed_roles}'
            )
        return current_user