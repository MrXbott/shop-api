from fastapi import FastAPI, HTTPException
from bson.errors import InvalidId

from app.api.v1 import users
from app.exceptions.exc import invalid_id_exception_handler, http_exception_handler
from app.middleware.logging import LoggingMiddleware

app = FastAPI()

app.add_exception_handler(InvalidId, invalid_id_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

app.add_middleware(LoggingMiddleware)

app.include_router(users.router, prefix='/api/v1')


