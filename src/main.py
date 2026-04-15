from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run

from .api.tracks import router as tracks_router
from .utils import cors_urls as sites

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=sites,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(tracks_router)


if __name__ == "__main__":
    try:
        run(app=app, host="127.0.0.1", port=8000)

    except KeyboardInterrupt:
        print("Exit")
