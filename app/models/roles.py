from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, PrimaryKeyConstraint
from typing import TYPE_CHECKING

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.users import UserModel


class RoleModel(Base):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=True)

    permissions: Mapped[list['PermissionModel']] = relationship(secondary='role_permissions', 
                                                           back_populates='roles', 
                                                           lazy='selectin',
                                                           )
    users: Mapped[list['UserModel']] = relationship('UserModel', 
                                                secondary='users_roles', 
                                                back_populates='roles',
                                                lazy='selectin' 
                                            )


class PermissionModel(Base):
    __tablename__ = 'permissions'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    resource: Mapped[str] = mapped_column(String(50), nullable=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=True)

    roles: Mapped[list['RoleModel']] = relationship(secondary='role_permissions', 
                                             back_populates='permissions', 
                                             lazy='selectin',
                                             )


class RolePermissionModel(Base):
    __tablename__ = 'role_permissions'

    role_id = mapped_column(ForeignKey('roles.id'), primary_key=True)
    permission_id = mapped_column(ForeignKey('permissions.id'), primary_key=True)


class UserRolesModel(Base):
    __tablename__ = 'users_roles'

    user_id = mapped_column(ForeignKey('users.id'), primary_key=True)
    role_id = mapped_column(ForeignKey('roles.id'), primary_key=True)

    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'role_id', name='users_roles_pkey'),
    )