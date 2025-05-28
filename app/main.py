from fastapi import FastAPI, HTTPException
from bson.errors import InvalidId

from app.api.v1 import users, products, orders
from app.exceptions.exc import register_exception_handlers
from app.middleware.logging import LoggingMiddleware

app = FastAPI()

register_exception_handlers(app)

app.add_middleware(LoggingMiddleware)

app.include_router(users.router, prefix='/api/v1')
app.include_router(products.router, prefix='/api/v1')
app.include_router(orders.router, prefix='/api/v1')


