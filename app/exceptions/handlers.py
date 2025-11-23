from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse

from app.exceptions.users import UserNotFound

from app.logger_config import logger

def register_exception_handlers(app: FastAPI):
    
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
