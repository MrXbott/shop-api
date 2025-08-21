import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.users import UserService
from app.schemas.users import UserRegister, UserCreate, UserUpdate, UserFromDB, UserQueryParams
from app.exceptions.users import UserNotFound, UserEmailAlreadyExists, UserNoUpdateData
from app.repos.postgres.users import UserRepoPostgres


@pytest.mark.asyncio
async def test_create_new_user(test_session: AsyncSession):
    repo = UserRepoPostgres(test_session)
    user_service = UserService(repo)

    user_data = UserRegister(
        first_name='New', 
        last_name='User', 
        email='newuser@example.com',
        password='Secret1!'
        )

    user = await user_service.create_new_user(user_data)

    assert isinstance(user, UserFromDB)
    assert user.email == user_data.email
    assert user.first_name == user_data.first_name
    assert user.id is not None


@pytest.mark.asyncio
async def test_create_new_user_duplicate_email(test_session):
    repo = UserRepoPostgres(test_session)
    user_service = UserService(repo)

    user_data = UserRegister(
        first_name='New', 
        last_name='User', 
        email='newuser@example.com',
        password='Secret1!'
        )
    
    await user_service.create_new_user(user_data)

    with pytest.raises(UserEmailAlreadyExists):
        await user_service.create_new_user(user_data)


@pytest.mark.asyncio
async def test_get_user_by_id(test_session):
    repo = UserRepoPostgres(test_session)
    user_service = UserService(repo)

    user_data = UserRegister(
        first_name='Mary', 
        last_name='M', 
        email='mary@example.com',
        password='Secret1!'
        )

    user = await user_service.create_new_user(user_data)
    user_found = await user_service.get_user_by_id(user.id)

    assert isinstance(user_found, UserFromDB)
    assert user_found.email == 'mary@example.com'


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(test_session):
    repo = UserRepoPostgres(test_session)
    user_service = UserService(repo)

    with pytest.raises(UserNotFound):
        await user_service.get_user_by_id(99999)


@pytest.mark.asyncio
async def test_get_user_by_email(test_session):
    repo = UserRepoPostgres(test_session)
    user_service = UserService(repo)

    user_data = UserRegister(
        first_name='Mike', 
        last_name='M', 
        email='mike@example.com',
        password='Secret1!'
        )

    await user_service.create_new_user(user_data)
    user = await user_service.get_user_by_email('mike@example.com')

    assert isinstance(user, UserFromDB)
    assert user.email == 'mike@example.com'


@pytest.mark.asyncio
async def test_get_user_by_email_not_found(test_session):
    repo = UserRepoPostgres(test_session)
    user_service = UserService(repo)

    with pytest.raises(UserNotFound):
        await user_service.get_user_by_email('notfound@example.com')


@pytest.mark.asyncio
async def test_get_users_by_params(test_session):
    repo = UserRepoPostgres(test_session)
    user_service = UserService(repo)

    params = UserQueryParams(role='user', limit=2, skip=1)
    users = await user_service.get_users_by_params(params)

    assert isinstance(users, list)
    assert len(users) == 2
    assert all(user.role == 'user' for user in users)


@pytest.mark.asyncio
async def test_count_users(test_session):
    repo = UserRepoPostgres(test_session)
    user_service = UserService(repo)

    count_before = await user_service.count_users()

    assert isinstance(count_before, int)
    assert count_before >= 0

    user_data = UserRegister(
        first_name='Bill', 
        last_name='B', 
        email='bill@example.com',
        password='Secret1!'
        )
    
    await user_service.create_new_user(user_data)
    count_after = await user_service.count_users()

    assert count_after == count_before + 1


@pytest.mark.asyncio
async def test_update_user(test_session):
    repo = UserRepoPostgres(test_session)
    user_service = UserService(repo)

    user_data = UserRegister(
        first_name='Dan', 
        last_name='D', 
        email='dan@example.com',
        password='Secret1!'
        )
    
    user = await user_service.create_new_user(user_data)

    user_data_update = UserUpdate(
        first_name='Danny', 
        last_name='Dine', 
        )
    
    updated_user = await user_service.update_user(user.id, user_data_update)

    assert isinstance(updated_user, UserFromDB)
    assert updated_user.first_name == 'Danny'
    assert updated_user.last_name == 'Dine'


@pytest.mark.asyncio
async def test_update_user_not_found(test_session):
    repo = UserRepoPostgres(test_session)
    user_service = UserService(repo)

    user_data_update = UserUpdate(first_name='NewFirstName')
    with pytest.raises(UserNotFound):
        await user_service.update_user(999, user_data_update)


@pytest.mark.asyncio
async def test_update_user_no_data(test_session):
    repo = UserRepoPostgres(test_session)
    user_service = UserService(repo)

    user_data = UserRegister(
        first_name='Danny', 
        last_name='D', 
        email='danny@example.com',
        password='Secret1!'
        )
    
    user = await user_service.create_new_user(user_data)

    with pytest.raises(UserNoUpdateData):
        await user_service.update_user(user.id, UserUpdate(**{}))


@pytest.mark.asyncio
async def test_delete_user(test_session):
    repo = UserRepoPostgres(test_session)
    user_service = UserService(repo)

    user_data = UserRegister(
        first_name='Delete', 
        last_name='D', 
        email='delete@example.com',
        password='Secret1!'
        )
    
    user = await user_service.create_new_user(user_data)

    result = await user_service.delete_user(user.id)
    assert result is True


@pytest.mark.asyncio
async def test_delete_user_not_found(test_session):
    repo = UserRepoPostgres(test_session)
    user_service = UserService(repo)

    with pytest.raises(UserNotFound):
        await user_service.delete_user(99999)
