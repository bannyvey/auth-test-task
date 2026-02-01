from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi_pagination import add_pagination

from src.api import router
from src.clients.redis import RedisClient
from src.exceptions.handlers import ErrorHandlerMiddleware, validation_exception_handler, http_exception_handler
from src.config.settings import get_settings


get_settings().logging.setup()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await RedisClient.init_pool()
    yield
    await RedisClient.close_pool()

app = FastAPI(title="Auth-Service", lifespan=lifespan)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler
)
app.add_exception_handler(
    HTTPException, http_exception_handler
)

app.add_middleware(ErrorHandlerMiddleware)


app.include_router(router)

add_pagination(app)