from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse

from .audio import AudioFile
from .main_logic import MainLogic

audio = AudioFile()
app = FastAPI()
logic = MainLogic()


@app.get('/hard')
async def hard(artist_name: str, rounds: int = 5, snippet_length_ms: int = 10000):
    return await logic.metadata_async(artist_name, rounds, snippet_length_ms)
    

@app.get('/medium')
async def medium(artist_name: str, rounds: int = 5, snippet_length_ms: int = 15000):
    return await logic.metadata_async(artist_name, rounds, snippet_length_ms)


@app.get('/easy')
async def easy(artist_name: str, rounds: int = 5, snippet_length_ms: int = 20000):
    return await logic.metadata_async(artist_name, rounds, snippet_length_ms)


@app.get('/snippet/{track_id}')
async def snippet(track_id: str | int, length_ms: int = Query(15000)):
    file = await logic.trim_track_async(track_id, length_ms)

    return StreamingResponse(
        file,
        media_type = "audio/mpeg",
        headers = {
            "Content-Disposition": f"inline; filename=snippet_{track_id}_{length_ms}ms.mp3",
            "Cache-Control": "public, max-age=1800"  # Кэшируем на 30 минут
        }
    )