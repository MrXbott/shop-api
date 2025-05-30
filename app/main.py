from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.v1 import users, products, orders
from app.exceptions.handlers import register_exception_handlers
from app.middleware.logging import LoggingMiddleware
from app.db.database import setup_indexes


@asynccontextmanager
async def lifespan(app: FastAPI):
    await setup_indexes()
    yield

app = FastAPI(lifespan=lifespan)

register_exception_handlers(app)

app.add_middleware(LoggingMiddleware)

app.include_router(users.router, prefix='/api/v1')
app.include_router(products.router, prefix='/api/v1')
app.include_router(orders.router, prefix='/api/v1')
