from pydantic import BaseModel, ConfigDict
from typing import Optional


class PermissionBase(BaseModel):
    name: str
    resource: str
    action: str
    description: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class PermissionResponse(PermissionBase):
    id: int
    
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class RoleCreate(RoleBase):
    permission_ids: list[int] = []

class RoleFromDB(RoleBase):
    id: int
    permissions: list[PermissionResponse] = []
    
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

