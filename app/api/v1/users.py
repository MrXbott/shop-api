from fastapi import APIRouter
from app.db.database import db

router = APIRouter(prefix='/user')

@router.get('/all')
async def get_all_users():
    users = db.get_collection('users').find()
    result = []
    async for user in users:
        user['_id'] = str(user['_id'])
        result.append(user)
    return {'users': result}

