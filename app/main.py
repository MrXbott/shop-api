from fastapi import FastAPI
from contextlib import asynccontextmanager
import os

from app.api.v1 import auth, users, products, orders
from app.exceptions.handlers import register_exception_handlers
from app.middleware.logging import LoggingMiddleware
from app.db.database import setup_indexes

API_PREFIX = os.getenv('API_PREFIX')

@asynccontextmanager
async def lifespan(app: FastAPI):
    await setup_indexes()
    yield

app = FastAPI(lifespan=lifespan)

register_exception_handlers(app)

app.add_middleware(LoggingMiddleware)

app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(users.router, prefix=API_PREFIX)
app.include_router(products.router, prefix=API_PREFIX)
app.include_router(orders.router, prefix=API_PREFIX)
