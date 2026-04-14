from logging import Logger
from typing import Annotated, Dict, List

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, StreamingResponse
from pydantic import BaseModel

from .audio import AudioFile
from .conf import CustomLogger
from .main_logic import MainLogic
from .utils import cors_urls as sites


class ContinueRequest(BaseModel):
    repeats: List[int | str]  # список ID уже показанных треков
    rounds: int = 5  # количество треков для нового раунда
    length_ms: int = 15000  # длина сниппета в миллисекундах


logger: Logger = CustomLogger(filename="webserver.log", loggerName="webserver")._logger
audio = AudioFile()
app = FastAPI()
logic = MainLogic()

app.add_middleware(
    CORSMiddleware,
    allow_origins=sites,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def test():
    return RedirectResponse(url="/docs")


@app.get("/get_tracks/{artist_name}")
async def difficulty_manager(
    artist_name: str,
    rounds: int = Query(5),
    length_ms: int = Query(15000),
) -> List[Dict]:
    audio._rotate_proxy()
    return await logic.metadata_async(artist_name, rounds, length_ms)


@app.get("/snippet")
async def snippet(
    track_id: str | int, length_ms: int = Query(15000)
) -> StreamingResponse:
    audio._rotate_proxy()
    file = await logic.trim_track_async(track_id, length_ms)

    return StreamingResponse(
        file,
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": f"inline; filename=snippet_{track_id}_{length_ms}ms.mp3",
            "Cache-Control": "public, max-age=1800",  # Кэшируем на 30 минут
        },
    )


@app.post("/continue/{artist_name}")
async def continue_game(artist_name: str, request: ContinueRequest):
    audio._rotate_proxy()
    return await logic.metadata_async(
        artist_name, request.rounds, request.length_ms, request.repeats
    )
