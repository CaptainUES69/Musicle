from logging import Logger
from typing import Dict, List

from fastapi import Query, APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..audio import AudioFile
from ..conf import CustomLogger
from ..methods import MethodsAudio


class ContinueRequest(BaseModel):
    repeats: List[int | str]  # список ID уже показанных треков
    rounds: int = 5  # количество треков для нового раунда
    length_ms: int = 15000  # длина сниппета в миллисекундах


logger: Logger = CustomLogger(filename="webserver.log", loggerName="webserver")._logger
audio = AudioFile()
methods = MethodsAudio()
router = APIRouter(prefix="tracks", tags=["tracks"])


@router.get("/get_tracks/{artist_name}")
async def difficulty_manager(
    artist_name: str,
    rounds: int = Query(5),
    length_ms: int = Query(15000),
) -> List[Dict]:
    return await methods.metadata_async(artist_name, rounds, length_ms)


@router.post("/continue/{artist_name}")
async def continue_game(artist_name: str, request: ContinueRequest):
    return await methods.metadata_async(
        artist_name, request.rounds, request.length_ms, request.repeats
    )


@router.get("/snippet")
async def snippet(
    track_id: str | int, length_ms: int = Query(15000)
) -> StreamingResponse:
    file = await methods.trim_track_async(track_id, length_ms)

    return StreamingResponse(
        file,
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": f"inline; filename=snippet_{track_id}_{length_ms}ms.mp3",
            "Cache-Control": "public, max-age=1800",  # Кэшируем на 30 минут
        },
    )
