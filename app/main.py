from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.v1 import auth, users, products, orders, categories
from app.exceptions.handlers import register_exception_handlers
from app.middleware.logging import LoggingMiddleware
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)

register_exception_handlers(app)

app.add_middleware(LoggingMiddleware)

app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(users.router, prefix=settings.api_prefix)
app.include_router(categories.router, prefix=settings.api_prefix)
app.include_router(products.router, prefix=settings.api_prefix)
app.include_router(orders.router, prefix=settings.api_prefix)
