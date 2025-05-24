from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from bson.errors import InvalidId

from app.logger_config import logger

async def invalid_id_exception_handler(request: Request, exc: InvalidId):
    logger.warning(f'Invalid ID: {request.url.path} - {exc}')
    return JSONResponse(
        status_code=400,
        content={'detail': 'Invalid ID format: it must be a 12-byte input or a 24-character hex string'}
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f'Http exception: {request.url.path} - {exc}')
    return JSONResponse(
        status_code=exc.status_code,
        content={'detail': exc.detail}
    )