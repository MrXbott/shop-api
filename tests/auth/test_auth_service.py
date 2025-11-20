import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, Mock, ANY, patch

from app.services.auth import AuthService
from app.exceptions.tokens import InvalidToken, ExpiredToken, InvalidTokenPayload, ExpiredToken, TokenNotFound
from app.exceptions.sessions import SessionNotFound, SessionException
from app.exceptions.users import UserUnauthorized, UserNotFound
from app.schemas.users import UserFromDB
from app.schemas.tokens import RefreshTokenFromDB, RefreshToken, TokenPayload
from app.utils.passwords import get_password_hash


@pytest.fixture
def mock_user():
    return UserFromDB(
        id=1,
        first_name='User',
        last_name='Userov',
        email='test@example.com',
        password_hash=get_password_hash('pass123'),
        role='user'
    )


@pytest.fixture
def auth_service():
    session_repo = AsyncMock()
    token_repo = AsyncMock()
    user_service = AsyncMock()

    service = AuthService(
        session_repo=session_repo,
        token_repo=token_repo,
        user_service=user_service,
        access_expire_minutes=15,
        refresh_expire_days=7,
        session_lifetime_days=30,
        secret_key='secret123',
        algorithm='HS256',
    )
    return service


# ----- decode tokens -----

@pytest.mark.asyncio
async def test_decode_token_valid(auth_service):
    payload = {
        'sub': '1', 
        'session_id': 'sess123',
        'jti': 'jti123',
        'scope': 'access', 
        'exp': int((datetime.now() + timedelta(minutes=1)).timestamp())
        }
    token = jwt.encode(payload, auth_service.secret_key, algorithm=auth_service.algorithm)

    decoded = auth_service.decode_token(token)

    assert decoded.sub == 1
    assert decoded.scope == 'access'


@pytest.mark.asyncio
async def test_decode_token_expired(auth_service):
    payload = {
        'sub': '1', 
        'session_id': 'sess123',
        'jti': 'jti123',
        'scope': 'access', 
        'exp': int((datetime.now() - timedelta(minutes=1)).timestamp())
        }
    token = jwt.encode(payload, auth_service.secret_key, algorithm=auth_service.algorithm)

    with pytest.raises(ExpiredToken):
        auth_service.decode_token(token)


@pytest.mark.asyncio
async def test_decode_token_invalid(auth_service):
    with pytest.raises(InvalidToken):
        auth_service.decode_token('not-a-token')

@pytest.mark.asyncio
async def test_decode_token_invalid_payload(auth_service):
    payload = {
        'sub': 'a', 
        'session_id': 'sess123',
        'jti': 'jti123',
        'scope': 'access', 
        'exp': int((datetime.now() + timedelta(minutes=1)).timestamp())
        }
    token = jwt.encode(payload, auth_service.secret_key, algorithm=auth_service.algorithm)

    with pytest.raises(InvalidTokenPayload):
        auth_service.decode_token(token)


# ----- create tokens -----

@pytest.mark.asyncio
async def test_create_access_token(auth_service):
    token = auth_service.create_access_token(user_id=1)
    decoded = auth_service.decode_token(token)

    assert decoded.sub == 1
    assert decoded.scope == 'access'



@pytest.mark.asyncio
async def test_create_refresh_token(auth_service):
    session_id = 'sess123'
    jti = 'abc123'

    token = auth_service.create_refresh_token(
        user_id=1, 
        session_id=session_id, 
        expires_at=datetime.now() + timedelta(minutes=1), 
        jti=jti
        )
    decoded = auth_service.decode_token(token)

    assert decoded.sub == 1
    assert decoded.session_id == session_id
    assert decoded.jti == jti
    assert decoded.scope == 'refresh'


# ----- auth user -----

@pytest.mark.asyncio
async def test_authenticate_user_success(auth_service, mock_user):
    auth_service.user_service.get_user_by_email.return_value = mock_user
    auth_service.user_service.verify_password.return_value = True

    user = await auth_service.authenticate_user('test@example.com', 'pass123')

    assert user.id == mock_user.id


@pytest.mark.asyncio
async def test_authenticate_user_not_found(auth_service):
    auth_service.user_service.get_user_by_email.side_effect = UserNotFound()

    with pytest.raises(UserNotFound):
        await auth_service.authenticate_user('x@x.com', 'pass')


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(auth_service, mock_user):
    auth_service.user_service.get_user_by_email.return_value = mock_user
    auth_service.user_service.verify_password.return_value = False

    with pytest.raises(UserUnauthorized):
        await auth_service.authenticate_user('test@example.com', 'wrong')



# ----- add refresh token -----

@pytest.mark.asyncio
async def test_add_refresh_token(auth_service):
    auth_service.token_repo.add_refresh_token.return_value = True
    auth_service.create_refresh_token = MagicMock(return_value='token123')

    token = await auth_service.add_refresh_token(user_id=1, session_id='some_session_id')

    assert token == 'token123'
    auth_service.token_repo.add_refresh_token.assert_awaited()



# ----- update refresh token -----

@pytest.mark.asyncio
async def test_update_refresh_token_success(auth_service):
    token = 'refresh.jwt.token'

    mock_payload = TokenPayload(
        sub='1',
        session_id='sess123',
        jti='oldjti123',
        scope='refresh',
        exp=int((datetime.now() + timedelta(days=1)).timestamp())
    )

    auth_service.decode_token = Mock(return_value=mock_payload)

    session_obj = MagicMock()
    session_obj.id = 'sess123'
    session_obj.is_active = True
    session_obj.expires_at = datetime.now() + timedelta(days=1)

    auth_service.session_repo.get_by_id = AsyncMock(return_value=session_obj)

    token_obj = MagicMock()
    token_obj.id = 'oldjti123'
    token_obj.is_used = False
    token_obj.expires_at = datetime.now() + timedelta(days=1)

    auth_service.token_repo.get_by_id = AsyncMock(return_value=token_obj)

    auth_service.token_repo.mark_as_used = AsyncMock()
    auth_service.token_repo.add_refresh_token = AsyncMock()

    auth_service.create_refresh_token = MagicMock(return_value='new_refresh')
    auth_service.create_access_token = MagicMock(return_value='new_access')

    result = await auth_service.update_refresh_token(token)

    assert isinstance(result, RefreshToken)
    assert result.access_token == 'new_access'
    assert result.refresh_token == 'new_refresh'

    auth_service.token_repo.mark_as_used.assert_awaited_once_with('oldjti123')
    auth_service.token_repo.add_refresh_token.assert_awaited()



@pytest.mark.asyncio
async def test_update_refresh_token_session_not_found(auth_service):
    token = 'refresh.jwt.token'

    mock_payload = TokenPayload(
        sub='1',
        session_id='sess123',
        jti='oldjti123',
        scope='refresh',
        exp=int((datetime.now() + timedelta(days=1)).timestamp())
    )

    auth_service.decode_token = Mock(return_value=mock_payload)

    auth_service.session_repo.get_by_id = AsyncMock(side_effect=SessionNotFound)

    with pytest.raises(SessionNotFound):
        await auth_service.update_refresh_token(token)


@pytest.mark.asyncio
async def test_update_refresh_token_token_not_found(auth_service):
    token = 'refresh.jwt.token'

    mock_payload = TokenPayload(
        sub='1',
        session_id='sess123',
        jti='oldjti123',
        scope='refresh',
        exp=int((datetime.now() + timedelta(days=1)).timestamp())
    )

    auth_service.decode_token = Mock(return_value=mock_payload)

    session_obj = MagicMock()
    session_obj.id = 'sess123'
    session_obj.is_active = True
    session_obj.expires_at = datetime.now() + timedelta(days=1)

    auth_service.session_repo.get_by_id = AsyncMock(return_value=session_obj)

    auth_service.token_repo.get_by_id = AsyncMock(side_effect=TokenNotFound)

    with pytest.raises(TokenNotFound):
        await auth_service.update_refresh_token(token)


# ----- login -----

@pytest.mark.asyncio
async def test_login_success(auth_service, mock_user):
    user_id = 1
    user_agent = 'TestAgent'
    ip = '127.0.0.1'
    session_expires_at = datetime.now() + timedelta(days=auth_service.session_lifetime_days)

    session_obj = MagicMock()
    session_obj.id = 'sess123'
    session_obj.user_id = user_id
    session_obj.expires_at = session_expires_at
    
    auth_service.session_repo.create_session = AsyncMock(return_value=session_obj)

    auth_service.create_refresh_token = Mock(return_value='refresh_token_123')
    auth_service.create_access_token = Mock(return_value='access_token_123')

    auth_service.token_repo.add_refresh_token = AsyncMock()

    access_token, refresh_token = await auth_service.login(user_id, user_agent, ip)

    assert access_token == 'access_token_123'
    assert refresh_token == 'refresh_token_123'

    auth_service.session_repo.create_session.assert_awaited_once_with(
        user_id,
        ANY,
        user_agent,
        ip
    )

    auth_service.token_repo.add_refresh_token.assert_awaited_once()

    auth_service.create_refresh_token.assert_called_once_with(
        user_id,
        session_obj.id,
        ANY,
        ANY
    )
    auth_service.create_access_token.assert_called_once_with(user_id)



# ----- logout -----

@pytest.mark.asyncio
async def test_logout_success(auth_service):
    session_id = 'sess123'

    auth_service.session_repo.revoke_session = AsyncMock()
    auth_service.token_repo.mark_as_used = AsyncMock()

    await auth_service.logout(session_id)

    auth_service.session_repo.revoke_session.assert_awaited_once_with(session_id)
    auth_service.token_repo.mark_as_used.assert_awaited_once_with(session_id)


@pytest.mark.asyncio
async def test_logout_session_not_found(auth_service):
    session_id = 'sess_not_exist'

    auth_service.session_repo.revoke_session = AsyncMock(side_effect=SessionNotFound())

    auth_service.token_repo.mark_as_used = AsyncMock()

    with pytest.raises(SessionNotFound):
        await auth_service.logout(session_id)

    auth_service.token_repo.mark_as_used.assert_not_awaited()


# ----- change password -----

@pytest.mark.asyncio
async def test_change_password_success(auth_service):
    user_id = 1
    new_password = 'new_password_123'
    new_password_hash = 'pwd_hash_123'

    with patch('app.services.auth.get_password_hash', return_value=new_password_hash):
        auth_service.user_service.repo.update_password = AsyncMock()
        await auth_service.change_password(user_id, new_password)

        auth_service.user_service.repo.update_password.assert_awaited_once_with(user_id, new_password_hash)


@pytest.mark.asyncio
async def test_change_password_user_not_found(auth_service):
    user_id = 999
    new_password = 'new_password_123'
    new_password_hash = 'hashed_new_password'

    with patch('app.services.auth.get_password_hash', return_value=new_password_hash):

        auth_service.user_service.repo.update_password = AsyncMock(side_effect=UserNotFound())

        with pytest.raises(UserNotFound):
            await auth_service.change_password(user_id, new_password)