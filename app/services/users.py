from app.schemas.users import UserCreate, UserFromDB, UserUpdate, UserQueryParams
from app.db.crud.users import UserCRUD
from app.services.base import BaseService

class User(BaseService[UserCreate, UserFromDB, UserUpdate, UserQueryParams]):
    crud_class = UserCRUD
    return_schema_class = UserFromDB
