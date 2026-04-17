from fastapi import APIRouter, HTTPException, Depends, status

from app.schemas.users import (UserRegisterByAdmin, 
                               UserFromDB, 
                               UserFromDBView,
                               UserUpdate, 
                               UserUpdateByAdmin,
                               ChangePasswordByUser, 
                               ChangePasswordByAdmin, 
                               UserQueryParams, 
                               UserProfile
                               )
from app.services.users import UserService
from app.services.auth import AuthService
from app.dependencies.users import get_current_user
from app.dependencies.services import get_user_service, get_auth_service
from app.dependencies.roles import RoleChecker, PermissionChecker
from app.exceptions.users import (UserNotFound, 
                                  CreateUserException, 
                                  UpdateUserException, 
                                  UserEmailAlreadyExists, 
                                  UserNoUpdateData
                                  )

from app.utils.passwords import verify_password

router = APIRouter(prefix='/users')
    
@router.get('/me', response_model=UserProfile, status_code=status.HTTP_200_OK)
async def get_my_profile(current_user: UserFromDB = Depends(get_current_user)):
    return current_user

@router.patch('/me', response_model=UserProfile, status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_user)])
async def update_my_profile(user_data: UserUpdate, user_service: UserService = Depends(get_user_service)):
    try:
        return await user_service.update_user(create_user.id, user_data)
    except (UserNotFound, UserNoUpdateData, UpdateUserException) as e:
        raise HTTPException(e.status_code, e.message)
    
@router.patch('/me/change_password', status_code=status.HTTP_200_OK)
async def change_own_password(data: ChangePasswordByUser, 
                          current_user: UserFromDB = Depends(get_current_user),
                          user_service: UserService = Depends(get_user_service),
                          auth_service: AuthService = Depends(get_auth_service)
                          ):
    
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail='Wrong current password')

    try:
        await user_service.change_password(current_user.id, data.new_password)
        await auth_service.revoke_all_sessions_for_user(current_user.id)
    except UserNotFound as e:
        raise HTTPException(e.status_code, e.message)

    return {'message': 'Password changed successfully'}


# ------ admin routes
@router.post('/', response_model=UserFromDBView, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RoleChecker(['admin']))])
async def create_user(user: UserRegisterByAdmin, user_service: UserService = Depends(get_user_service)):
    try:
        return await user_service.create_new_user(user)
    except (CreateUserException, UserNotFound, UserEmailAlreadyExists) as e:
        raise HTTPException(e.status_code, e.message)

@router.get('/', response_model=list[UserFromDBView], status_code=status.HTTP_200_OK, dependencies=[Depends(RoleChecker(['admin']))])
async def get_users(params: UserQueryParams = Depends(), user_service: UserService = Depends(get_user_service)):
    return await user_service.get_users_by_params(params)

@router.get('/count', status_code=status.HTTP_200_OK, dependencies=[Depends(RoleChecker(['admin']))])
async def get_users_count(user_service: UserService = Depends(get_user_service)):
    return {'users_count': await user_service.count_users()}

@router.get('/{user_id}', response_model=UserFromDBView, status_code=status.HTTP_200_OK, dependencies=[Depends(RoleChecker(['admin']))])
async def get_user_profile_by_id(user_id: int, user_service: UserService = Depends(get_user_service)):
    try:
        return await user_service.get_user_by_id(user_id)
    except UserNotFound as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))

@router.patch('/{user_id}', response_model=UserFromDBView, status_code=status.HTTP_200_OK, dependencies=[Depends(RoleChecker(['admin']))])
async def update_user_profile_by_id(user_id: int, user_data: UserUpdateByAdmin, user_service: UserService = Depends(get_user_service)):
    try:
        return await user_service.update_user(user_id, user_data)
    except (UserNotFound, UserNoUpdateData, UpdateUserException) as e:
        raise HTTPException(e.status_code, e.message)

@router.delete('/{user_id}', status_code=status.HTTP_200_OK, dependencies=[Depends(RoleChecker(['admin']))])
async def delete_user_by_id(user_id: int, user_service: UserService = Depends(get_user_service)):
    try:
        await user_service.delete_user(user_id)
        return {'message': 'User deleted'}
    except UserNotFound as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))
    
@router.patch('/{user_id}/change_password', status_code=status.HTTP_200_OK, dependencies=[Depends(RoleChecker(['admin']))])
async def change_password(user_id: int, 
                          data: ChangePasswordByAdmin, 
                          user_service: UserService = Depends(get_user_service),
                          auth_service: AuthService = Depends(get_auth_service)
                          ):
    try:
        await user_service.change_password(user_id, data.new_password)
        await auth_service.revoke_all_sessions_for_user(user_id)
    except UserNotFound as e:
        raise HTTPException(e.status_code, e.message)

    return {'message': 'Password changed successfully'}
    
    