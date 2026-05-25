from asyncio import sleep

from fastapi import status
from sqlalchemy import and_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import load_only
from sqlalchemy.orm.exc import StaleDataError

from .core import AsyncSessionLocal
from .models import Users
from .utils import DifficultyEnum


async def users_create(
    nickname: str,
    artist: str,
    difficulty: DifficultyEnum = DifficultyEnum.Unknown,
    score: int = 0,
) -> Users:
    """Создание пользователя

    :param nickname: Имя игрока
    :type nickname: str
    :param artist: Имя Артиста
    :type artist: str
    :param difficulty: Сложность игры, по умолчанию равен DifficultyEnum.Unknown
    :type difficulty: DifficultyEnum, необязательно
    :param score: Очки игрока, по умолчанию равен 0
    :type score: int, необязательно
    :raises e: Ошибка при создании пользователя (IntegrityError, ValueError)
    :return: Запись с данными пользователя
    :rtype: Users
    """
    async with AsyncSessionLocal() as session:
        async with session.begin():
            user = Users(
                nickname=nickname,
                artist=artist,
                difficulty=difficulty.value,
                score=score,
            )
            session.add(user)

            try:
                await session.commit()
                return user

            except (IntegrityError, ValueError) as e:
                await session.rollback()
                raise e


async def users_read_current(
    nickname: str, artist: str, difficulty: DifficultyEnum
) -> Users:
    """Поиск пользователя по данным

    :param nickname: Имя игрока
    :type nickname: str
    :param artist: Имя артиста
    :type artist: str
    :param difficulty: Сложность игры
    :type difficulty: DifficultyEnum
    :return: Строка игрока
    :rtype: Users
    """
    async with AsyncSessionLocal() as session:
        async with session.begin():
            user_search = (
                select(Users)
                .options(load_only(Users.id))
                .where(
                    and_(
                        Users.nickname == nickname,
                        Users.artist == artist,
                        Users.difficulty == difficulty.value,
                    )
                )
            )
            result = await session.execute(user_search)
            return result.scalar_one_or_none()


async def users_read_top(limit: int) -> list[Users]:
    """Считывание Топ N игроков

    :param limit: Предел игроков которых нужно выбрать
    :type limit: int
    :return: Лист со значениями игроков (Никнейм, Очки)
    :rtype: list[Users]
    """
    async with AsyncSessionLocal() as session:
        async with session.begin():
            top = (
                select(Users)
                .options(load_only(Users.nickname, Users.score))
                .order_by(Users.score.desc())
                .limit(limit)
            )
            result = await session.execute(top)
            return list(result.scalars().all())


async def users_read_top_artist(limit: int, artist: str) -> list[Users]:
    """Считывание топа игроков по артисту

    :param limit: Предел игроков которых нужно выбрать
    :type limit: int
    :param artist: Имя артиста
    :type artist: str
    :return: Лист со значениями игроков (Никнейм, Очки)
    :rtype: list[Users]
    """
    async with AsyncSessionLocal() as session:
        async with session.begin():
            top = (
                select(Users)
                .options(load_only(Users.nickname, Users.artist, Users.score))
                .where(Users.artist == artist)
                .order_by(Users.score.desc())
                .limit(limit)
            )
            result = await session.execute(top)
            return list(result.scalars().all())


async def users_update_score(
    nickname: str,
    artist: str,
    difficulty: DifficultyEnum,
    score: int,
    max_retries: int = 3,
) -> Users:
    """Обновление очков у пользователя

    :param nickname: Имя игрока
    :type nickname: str
    :param artist: Имя артиста
    :type artist: str
    :param difficulty: Сложность игры
    :type difficulty: DifficultyEnum
    :param score: Очки игрока
    :type score: int
    :param max_retries: Максимальное кол-во попыток, по умолчанию равно 3
    :type max_retries: int, опционально
    :return: Строка с пользовательскими данными
    :rtype: Users
    """
    for attempt in range(max_retries):
        async with AsyncSessionLocal() as session:
            async with session.begin():
                user_search = (
                    update(Users)
                    .where(
                        and_(
                            Users.nickname == nickname,
                            Users.artist == artist,
                            Users.difficulty == difficulty.value,
                        )
                    )
                    .values(score=score)
                    .returning(Users)
                )
                result = await session.execute(user_search)
                user: Users = result.scalar_one_or_none()
                if not user:
                    return

                user.score = score

                try:
                    await session.commit()
                    return user

                except (
                    StaleDataError
                ):  # Ошибка изменения данных, откатываем транзакцию и пробуем заново
                    await session.rollback()
                    if attempt == max_retries - 1:
                        raise
                    await sleep(0.1 * (attempt + 1))

    return


async def upsert_user(
    nickname: str,
    artist: str,
    difficulty: DifficultyEnum,
    score: int,
) -> int:
    """Добавить/обновить пользователя

    :param nickname: Имя пользователя
    :type nickname: str
    :param artist: Имя артиста
    :type artist: str
    :param difficulty: Сложность игры
    :type difficulty: DifficultyEnum
    :param score: Кол-во очков
    :type score: int
    :return: Значения http кода
    :rtype: int
    """
    user = await users_read_current(
        nickname=nickname,
        artist=artist,
        difficulty=difficulty,
    )
    try:
        if not user:
            await users_create(
                nickname=nickname,
                artist=artist,
                difficulty=difficulty,
                score=score,
            )
            return status.HTTP_201_CREATED

        update = await users_update_score(
            nickname=nickname,
            artist=artist,
            difficulty=difficulty,
            score=score,
        )
        if update:
            return status.HTTP_200_OK

        else:
            return status.HTTP_409_CONFLICT

    except ValueError:
        return status.HTTP_400_BAD_REQUEST
