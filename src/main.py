from asyncio import run as async_run
from os import getenv

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run as uvicorn_run

from .api.leaderboard import router as leaderboard_router
from .api.tracks import router as tracks_router
from .database.core import init_db
from .utils import cors_urls as sites
from .conf import CustomLogger
from logging import Logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield  # Приложение работает
    logger.info("Unicorn worker is downed")


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=sites,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

routers = [tracks_router, leaderboard_router]
for router in routers:
    app.include_router(router)

logger: Logger = CustomLogger("audio")._logger


if __name__ == "__main__":
    host = getenv("HOST", "127.0.0.1")
    port = int(getenv("PORT", 8000))
    is_dev = getenv("APP_MODE", "dev") == "dev"

    uvicorn_run(
        app="src.main:app" if is_dev else app,
        host=host,
        port=port,
        reload=is_dev,
        log_level="debug" if is_dev else "info",
    )
