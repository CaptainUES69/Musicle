from logging import Logger

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ..conf import CustomLogger
from ..database.methods import (
    upsert_user,
    users_read_top,
    users_read_top_artist,
)
from ..database.utils import DifficultyEnum


class UserModel(BaseModel):
    nickname: str
    artist: str
    difficulty: DifficultyEnum = DifficultyEnum.Unknown.value
    score: int


logger: Logger = CustomLogger("leaderboard")._logger
router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.post("/user")
async def create_update(user: UserModel):
    status_code = await upsert_user(
        nickname=user.nickname,
        artist=user.artist,
        difficulty=user.difficulty,
        score=user.score,
    )

    if status_code == 200:
        return JSONResponse(content="Updated succesfully", status_code=status_code)

    elif status_code == 201:
        return JSONResponse(content="Created succesfully", status_code=status_code)

    else:
        return JSONResponse(content="Data conflict try again", status_code=status_code)


@router.get("/top")
async def get(limit: int = Query(10)):
    return await users_read_top(limit=limit)


@router.get("/top_artist/{artist_name}")
async def get(artist_name: str, limit: int = Query(10)):
    return await users_read_top_artist(limit=limit, artist=artist_name)
