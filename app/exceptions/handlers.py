from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from pymongo.errors import DuplicateKeyError, PyMongoError
from bson.errors import InvalidId

from app.exceptions.users import UserNotFound

from app.logger_config import logger

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(InvalidId)
    async def invalid_id_exception_handler(request: Request, exc: InvalidId):
        logger.warning(f'Invalid ID: {request.url.path} - {exc}')
        return JSONResponse(
            status_code=400,
            content={'detail': 'Invalid ID format: it must be a 12-byte input or a 24-character hex string'}
        )
    
    @app.exception_handler(UserNotFound)
    async def user_not_found_handler(request: Request, exc: UserNotFound):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'detail': exc.message}
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.warning(f'Http exception: {request.url.path} - {exc}')
        return JSONResponse(
            status_code=exc.status_code,
            content={'detail': exc.detail}
        )

    @app.exception_handler(DuplicateKeyError)
    async def duplicate_key_exception_handler(request: Request, exc: DuplicateKeyError):
        logger.warning(f'Duplicate field: {request.url.path} - {exc}')
        return JSONResponse(
            status_code=409,
            content={'detail': 'Duplicate key error: a user with this value already exists'}
        )

    @app.exception_handler(PyMongoError)
    async def pymongo_exception_handler(request: Request, exc: PyMongoError):
        logger.warning(f'Database error: {request.url.path} - {exc}')
        return JSONResponse(
            status_code=500,
            content={'detail': f'Database error: {str(exc)}'}
        )