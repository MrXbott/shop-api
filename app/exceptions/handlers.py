from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.exceptions.users import UserNotFound

from app.logger_config import logger

ERROR_MESSAGES = {
    'value_error.missing': 'This field is required',
    'value_error.email': 'Enter a valid email address',
    'string_pattern_mismatch': 'The string can only contain letters and hyphens'
}

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

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        custom_errors = []
        for error in exc.errors():
            err_type = error.get('type')
            field_name = error.get('loc')[-1]
            
            message = ERROR_MESSAGES.get(err_type, error.get('msg'))
            custom_errors.append({'field': field_name, 'message': message})
        
        return JSONResponse(
            status_code=422,
            content={'status': 'error', 'errors': custom_errors}
        )