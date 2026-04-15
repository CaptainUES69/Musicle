from asyncio import run as async_run

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run as uvicorn_run

from .api.leaderboard import router as leaderboard_router
from .api.tracks import router as tracks_router
from .database.core import init_db
from .utils import cors_urls as sites

app = FastAPI()
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


if __name__ == "__main__":
    try:
        async_run(init_db())
        uvicorn_run(app=app, host="127.0.0.1", port=8000)

    except KeyboardInterrupt:
        print("Exit")
