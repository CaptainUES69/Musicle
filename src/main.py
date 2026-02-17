from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse

from .audio import AudioFile
from .main_logic import MainLogic
from .conf import Logging
from typing import List, Dict, Annotated

from pydantic import BaseModel

logger = Logging(filename='webserver.log',loggerName='webserver')
audio = AudioFile()
app = FastAPI()
logic = MainLogic()




@app.get('/hard/{artist_name}')
async def hard(
    artist_name: str, 
    rounds: int = Query(5), 
    length_ms: int = Query(10000)
) -> List[Dict]:
    return await logic.metadata_async(artist_name, rounds, length_ms)
    

@app.get('/medium/{artist_name}')
async def medium(
    artist_name: str, 
    rounds: int = 5, 
    length_ms: int = Query(15000)
) -> List[Dict]:
    return await logic.metadata_async(artist_name, rounds, length_ms)


@app.get('/easy/{artist_name}')
async def easy(
    artist_name: str, 
    rounds: int = 5, 
    length_ms: int = Query(20000)
) -> List[Dict]:
    return await logic.metadata_async(artist_name, rounds, length_ms)


@app.get('/snippet/{track_id}')
async def snippet(
    track_id: str | int,
    length_ms: int = Query(15000)
) -> StreamingResponse:
    file = await logic.trim_track_async(track_id, length_ms)

    return StreamingResponse(
        file,
        media_type = "audio/mpeg",
        headers = {
            "Content-Disposition": f"inline; filename=snippet_{track_id}_{length_ms}ms.mp3",
            "Cache-Control": "public, max-age=1800"  # Кэшируем на 30 минут
        }
    )