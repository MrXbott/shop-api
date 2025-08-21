import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repos.postgres.users import UserRepoPostgres
from app.schemas.users import UserCreate, UserUpdate, UserFromDB
from app.exceptions.users import UserNotFound, UserEmailAlreadyExists, UserNoUpdateData


@pytest.mark.asyncio
async def test_create_user_success(test_session: AsyncSession):
    repo = UserRepoPostgres(test_session)
    user_data = UserCreate(
        first_name='Test', 
        last_name='Testov', 
        email='test@example.com',
        password_hash='hashed_password',
        role='user'
        )
    
    user = await repo.create(user_data)

    assert user.id is not None
    assert user.email == 'test@example.com'


@pytest.mark.asyncio
async def test_create_user_duplicate_email(test_session: AsyncSession):
    repo = UserRepoPostgres(test_session)
    user_data = UserCreate(
        first_name='Test', 
        last_name='Testov', 
        email='test@example.com',
        password_hash='hashed_password',
        role='user'
        )
    
    await repo.create(user_data)

    with pytest.raises(UserEmailAlreadyExists):
        await repo.create(user_data)


@pytest.mark.asyncio
async def test_get_by_id_user_found(test_session: AsyncSession):
    repo = UserRepoPostgres(test_session)
    user_data = UserCreate(
        first_name='Mary', 
        last_name='M', 
        email='mary@example.com',
        password_hash='hashed_password',
        role='user'
        )
    
    user = await repo.create(user_data)
    result = await repo.get_by_id(user.id)

    assert result.email == user.email


@pytest.mark.asyncio
async def test_get_by_id_user_not_found(test_session: AsyncSession):
    repo = UserRepoPostgres(test_session)

    with pytest.raises(UserNotFound):
        await repo.get_by_id(99999)


@pytest.mark.asyncio
async def test_get_by_email_user_found(test_session: AsyncSession):
    repo = UserRepoPostgres(test_session)
    user_data = UserCreate(
        first_name='John', 
        last_name='J', 
        email='john@example.com',
        password_hash='hashed_password',
        role='user'
        )
    
    await repo.create(user_data)
    result = await repo.get_by_email('john@example.com')

    assert result.email == 'john@example.com'


@pytest.mark.asyncio
async def test_get_by_email_user_not_found(test_session: AsyncSession):
    repo = UserRepoPostgres(test_session)
    with pytest.raises(UserNotFound):
        await repo.get_by_email('notfound@example.com')


@pytest.mark.asyncio
async def test_get_by_params(test_session: AsyncSession):
    repo = UserRepoPostgres(test_session)
    users = await repo.get_by_params(params={}, limit=2, skip=2)
    
    assert len(users) == 2
    

@pytest.mark.asyncio
async def test_count(test_session: AsyncSession):
    repo = UserRepoPostgres(test_session)
    count_before = await repo.count()
    assert isinstance(count_before, int)
    assert count_before >= 0
    
    user_data = UserCreate(
        first_name='Bill', 
        last_name='B', 
        email='bill@example.com',
        password_hash='hashed_password',
        role='user'
        )
    
    await repo.create(user_data)
    count_after = await repo.count()

    assert count_after == count_before + 1


@pytest.mark.asyncio
async def test_update_user_success(test_session: AsyncSession):
    repo = UserRepoPostgres(test_session)
    user_data = UserCreate(
        first_name='Dan', 
        last_name='D', 
        email='dan@example.com',
        password_hash='hashed_password',
        role='user'
        )

    user = await repo.create(user_data)

    user_data_update = UserUpdate(
        first_name='Danny', 
        last_name='Dine', 
        )

    updated_user = await repo.update_user(user.id, user_data_update)

    assert updated_user.first_name == 'Danny'
    assert updated_user.last_name == 'Dine'


@pytest.mark.asyncio
async def test_update_user_not_found(test_session: AsyncSession):
    repo = UserRepoPostgres(test_session)
    with pytest.raises(UserNotFound):
        await repo.update_user(99999, UserUpdate(first_name='NewFirstName'))

@pytest.mark.asyncio
async def test_update_user_no_data(test_session: AsyncSession):
    repo = UserRepoPostgres(test_session)
    user_data = UserCreate(
        first_name='Danny', 
        last_name='D', 
        email='danny@example.com',
        password_hash='hashed_password',
        role='user'
        )

    user = await repo.create(user_data)

    with pytest.raises(UserNoUpdateData):
        await repo.update_user(user.id, UserUpdate(**{}))


@pytest.mark.asyncio
async def test_delete_by_id_success(test_session: AsyncSession):
    repo = UserRepoPostgres(test_session)
    user_data = UserCreate(
        first_name='Delete', 
        last_name='D', 
        email='delete@example.com',
        password_hash='hashed_password',
        role='user'
        )

    user = await repo.create(user_data)
    result = await repo.delete(user.id)

    assert result is True


@pytest.mark.asyncio
async def test_delete_by_email_success(test_session: AsyncSession):
    repo = UserRepoPostgres(test_session)
    user_data = UserCreate(
        first_name='Delete', 
        last_name='D', 
        email='delete@example.com',
        password_hash='hashed_password',
        role='user'
        )
    
    await repo.create(user_data)
    result = await repo.delete('delete@example.com')

    assert result is True


@pytest.mark.asyncio
async def test_delete_user_not_found(test_session: AsyncSession):
    repo = UserRepoPostgres(test_session)
    with pytest.raises(UserNotFound):
        await repo.delete(99999)

