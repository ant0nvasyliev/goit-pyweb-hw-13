from ipaddress import ip_address
from typing import Callable
import redis.asyncio as redis
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from contextlib import asynccontextmanager

from src.routes import contacts, auth, users
from src.conf.config import config


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa

    redis_client = await redis.Redis(
        host=config.REDIS_DOMAIN, port=config.REDIS_PORT, db=0, password=config.REDIS_PASSWORD
    )
    await FastAPILimiter.init(redis_client)

    yield

    await redis_client.close()


app = FastAPI(lifespan=lifespan)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

ALLOWED_IPS = [ip_address('192.168.1.0'), ip_address('172.16.0.0'), ip_address("127.0.0.1")]


@app.middleware("http")
async def limit_access_by_ip(request: Request, call_next: Callable):
    ip = ip_address(request.client.host)
    if ip not in ALLOWED_IPS:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "Not allowed IP address"})
    response = await call_next(request)
    return response


# # Список заблокованих IP-адрес
# banned_ips = [ip_address("192.168.123.45"), ip_address("10.45.67.89"), ip_address("172.16.250.10")]
#
# # Middleware для блокування доступу для заблокованих IP-адрес
# @app.middleware("http")
# async def ban_ips(request: Request, call_next: Callable):
#     ip = ip_address(request.client.host)  # Отримуємо IP-адресу клієнта
#     if ip in banned_ips:  # Якщо IP у списку заблокованих
#         return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"})
#     response = await call_next(request)  # Продовжуємо обробку запиту
#     return response


app.include_router(auth.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(users.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Welcome to the Contacts API!"}
