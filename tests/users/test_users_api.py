import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock

from app.schemas.users import UserRegister, UserRegisterByAdmin, UserUpdate, UserFromDB
from app.services.users import UserService
from app.exceptions.users import UserNotFound, UserNoUpdateData
from app.main import app

BASE_URL = 'http://0.0.0.0:8000/api/v1'

@pytest.fixture
def mock_admin():
    return {
        'id': 1,
        'first_name': 'Admin', 
        'last_name': 'Adminov', 
        'email': 'admin@example.com',
        'password_hash': 'hashed_password',
        'role': 'admin'
    }


@pytest.fixture
def mock_user():
    return {
        'id': 2,
        'first_name': 'User', 
        'last_name': 'Userov', 
        'email': 'user@example.com',
        'password_hash': 'hashed_password',
        'role': 'user'
    }


@pytest.fixture(autouse=True)
def override_user_service(mock_user):
    service = AsyncMock(spec=UserService)
    service.get_user_by_email.return_value = None
    service.create_new_user.return_value = UserFromDB(**mock_user)
    service.get_users_by_params.return_value = [UserFromDB(**mock_user)]
    service.count_users.return_value = 1
    service.get_user_by_id.return_value = UserFromDB(**mock_user)
    service.update_user.return_value = UserFromDB(**mock_user)
    service.delete_user.return_value = True
    app.state._test_user_service = service
    return service


@pytest.fixture(autouse=True)
def override_dependencies(override_user_service, mock_user, mock_admin):
    app.dependency_overrides = {}

    def get_current_user():
        return mock_user
    
    def get_admin_user():
        return mock_admin

    from app.dependencies.services import get_user_service
    from app.dependencies.users import get_current_user as gcu, get_admin_user as gau

    app.dependency_overrides[gcu] = get_current_user
    app.dependency_overrides[gau] = get_admin_user
    app.dependency_overrides[get_user_service] = lambda: override_user_service

    yield
    app.dependency_overrides = {}

@pytest.mark.anyio
async def test_get_my_profile():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        response = await ac.get('/users/me')
        assert response.status_code == 200
        


@pytest.mark.anyio
async def test_create_user_by_admin():
    data = {
            'first_name': 'User', 
            'last_name': 'Userov', 
            'email': 'user@example.com',
            'password': 'secret',
            'role': 'user'
        }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        response = await ac.post('/users/', json=data)
        assert response.status_code == 201
        assert response.json()['email'] == 'user@example.com'


@pytest.mark.anyio
async def test_get_users_by_params():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        response = await ac.get('/users/')
        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.anyio
async def test_get_users_count():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        response = await ac.get('/users/count')
        assert response.status_code == 200
        assert response.json()['users_count'] == 1


@pytest.mark.anyio
async def test_get_user_by_id():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        response = await ac.get('/users/2')
        assert response.status_code == 200
        assert response.json()['email'] == 'user@example.com'


@pytest.mark.anyio
async def test_update_user_profile():
    data = {
            'first_name': 'User'
            }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        response = await ac.patch('/users/2', json=data)
        assert response.status_code == 200
        assert response.json()['first_name'] == 'User' 

@pytest.mark.anyio
async def test_update_user_profile_not_found():
    app.state._test_user_service.update_user.return_value = None
    app.state._test_user_service.update_user.side_effect = UserNotFound()
    data = {
            'first_name': 'User'
            }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        response = await ac.patch('/users/99999', json=data)
        assert response.status_code == 404
        assert response.json()['detail'] == 'User not found'


@pytest.mark.anyio
async def test_update_user_profile_no_data():
    app.state._test_user_service.update_user.return_value = None
    app.state._test_user_service.update_user.side_effect = UserNoUpdateData()
    data = {}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        response = await ac.patch('/users/99999', json=data)
        assert response.status_code == 400


@pytest.mark.anyio
async def test_delete_user():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        response = await ac.delete('/users/2')
        assert response.status_code == 200
        assert response.json()['message'] == 'User deleted'
        
