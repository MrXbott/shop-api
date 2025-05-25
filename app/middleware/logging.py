import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.logger_config import logger

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = round(time.time() - start, 3)

        msg = f'{request.method} {request.url.path} - {response.status_code} - {duration}s'

        if response.status_code < 400:
            logger.info(msg)
        elif 400 <= response.status_code < 500:
            logger.warning(msg)
        else:
            logger.error(msg)

        return response
