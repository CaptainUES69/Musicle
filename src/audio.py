from functools import wraps
from io import BytesIO
from json import load
from logging import Logger
from os import getenv
from random import randint
from typing import List, Optional

from dotenv import load_dotenv
from pydub import AudioSegment
from yandex_music import Client, ClientAsync
from yandex_music.artist.artist import Artist
from yandex_music.exceptions import InvalidBitrateError, NetworkError
from yandex_music.track.track import Track
from yandex_music.utils.request import Request
from yandex_music.utils.request_async import Request as RequestAsync

from .conf import CustomLogger
from logging import WARNING


class AudioFile:
    """
    Класс для работы с YandexMusicApi и полученными аудиофайлами
    """

    _proxy_list: list[str]
    client: Client
    clientAsync: ClientAsync = None
    logger: Logger = CustomLogger("audio")._logger

    # Внутренние методы

    def __init__(self):
        load_dotenv(override=True)
        self.client = Client(getenv("YANDEX_TOKEN")).init()
        with open("src/proxy_list.json", "r", encoding="utf-8") as f:
            self._proxy_list = load(f)["proxy"]

    @staticmethod
    def rotate_proxy_sync(func):
        """
        Синхронный декоратор:
        1. Сначала пытается выполнить запрос БЕЗ прокси.
        2. При NetworkError перебирает прокси из self._proxy_list,
           пересоздаёт clientAsync и повторяет вызов.
        3. Если все прокси не сработали – выбрасывает NetworkError.
        """

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except NetworkError as e:
                self.logger.warning(f"Без прокси ошибка: {e}. Переходим к прокси...")

            for proxy in self._proxy_list:
                try:
                    self.logger.info(f"Пробуем прокси (sync): {proxy}")

                    self.clientAsync = Client(
                        token=getenv("YANDEX_TOKEN"),
                        request=Request(proxy_url=proxy, timeout=15),
                    ).init()

                    return func(self, *args, **kwargs)

                except NetworkError as e:
                    self.logger.warning(f"Прокси {proxy} не ответил (sync): {e}")
                    continue

                except Exception as e:
                    self.logger.critical(
                        f"Неизвестная ошибка (sync) на прокси {proxy}: {e}"
                    )
                    raise

            raise NetworkError("Все прокси из списка недоступны (sync)")

        return wrapper

    @staticmethod
    def rotate_proxy_async(func):
        """
        Асинхронный декоратор:
        1. Сначала пытается выполнить запрос БЕЗ прокси.
        2. При NetworkError перебирает прокси из self._proxy_list,
           пересоздаёт clientAsync и повторяет вызов.
        3. Если все прокси не сработали – выбрасывает NetworkError.
        """

        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            try:
                return await func(self, *args, **kwargs)

            except NetworkError as e:
                self.logger.warning(f"Без прокси ошибка: {e}. Переходим к прокси...")

            for proxy in self._proxy_list:
                try:
                    self.logger.info(f"Пробуем прокси (async): {proxy}")

                    self.clientAsync = await ClientAsync(
                        token=getenv("YANDEX_TOKEN"),
                        request=RequestAsync(proxy_url=proxy, timeout=15),
                    ).init()

                    return await func(self, *args, **kwargs)

                except NetworkError as e:
                    self.logger.warning(f"Прокси {proxy} не ответил (async): {e}")
                    continue

                except Exception as e:
                    self.logger.critical(
                        f"Неизвестная ошибка (async) на прокси {proxy}: {e}"
                    )
                    raise

            raise NetworkError("Все прокси из списка недоступны (async)")

        return wrapper

    async def _ensure_async_client(self) -> None:
        """Создание асинхронного клиента"""
        if self.clientAsync is None:
            self.clientAsync = ClientAsync(getenv("YANDEX_TOKEN"))
            await self.clientAsync.init()
            self.logger.info("Client created succefully")

    # Основные методы

    @rotate_proxy_sync
    def get_track_by_id(self, track_ids: List[str | int] | int | str) -> List[Track]:
        """
        Возвращает список объектов Track по их id

        :param track_ids: _description_. id треков
        :type track_ids: List[str | int] | int | str
        :return: Список с полученными треками
        :rtype: List[Track]
        """

        tracks = self.client.tracks(track_ids)
        self.logger.info(f"{len(tracks)} треков найдено")
        return tracks

    @rotate_proxy_sync
    def get_bytes(self, track: Track, bitrate_in_kbps: int = 192) -> bytes:
        """
        Возвращает объект Track в виде байтов

        :param track: Трек для преобразования
        :type track: Track
        :param bitrate_in_kbps: Возможные значения: `64`, `128`, `192`, `320`.
        :type bitrate_in_kbps: int
        :return: Трек в виде байтов
        :rtype: bytes
        """
        try:
            self.logger.info(
                f"Скачиваем трек {track.title} с битрейтом {bitrate_in_kbps}"
            )
            return track.download_bytes(bitrate_in_kbps=bitrate_in_kbps)

        except InvalidBitrateError:
            self.logger.info(
                f"Ошибка скачивания {track.title} с битрейтом {bitrate_in_kbps} скачиваем с битрейтом 192"
            )
            return track.download_bytes(bitrate_in_kbps=192)

    @rotate_proxy_sync
    def search_artist(self, artist_name: str) -> Optional[List[Artist]]:
        """
        Возвращает список найденных артистов

        :param input: Имя артиста
        :type input: str
        :return: Список артистов
        :rtype: List[Artist] | None
        """

        search = self.client.search(artist_name, type_="artist")

        if not search or not search.artists:
            self.logger.warning(f"Артиста {artist_name} не найдено")
            return None

        self.logger.info(f"Найдены следующие артисты {search.artists.results[:-1]}")
        return search.artists.results

    def get_tracks_from_artist(
        self, artist: Artist, tracks_count: int = 200
    ) -> Optional[List[Track]]:
        """
        Получает треки у объекта `artist`

        :param artist: Артист с которого будут получены треки
        :type artist: Artist
        :param tracks_count: Кол-во получаемых треков по умолчанию: `20`
        :type tracks_count: int
        :return: Список треков
        :rtype: List[Track] | None
        """

        artistTracks = artist.getTracks(page_size=tracks_count)

        if not artistTracks:
            return None

        self.logger.info(f"Найдены следующие треки: {artistTracks.tracks}")
        return artistTracks.tracks

    def choose_tracks(
        self, tracks: list[Track], count: int, repeats: set[int | str] = None
    ) -> List[Track]:
        """
        Выбирает треки из списка без повторений

        :param tracks: Список всех треков из которых выбирается `count` кол-во треков
        :type tracks: list[Track]
        :param count: Количество нужных треков
        :type count: int
        :param repeats: Список с ID треков которые нужно отфильтровать
        :type repeats: set[int]
        :return: Лист уникальных треков
        :rtype: List[Track]
        """
        if repeats is None:
            repeats = set()
        tracks_id: list[str | int] = []
        tracks_list: list[Track] = []

        self.logger.info("Начинается отбор треков")
        while len(tracks_list) < count:
            number = randint(0, len(tracks) - 1)

            if tracks[number].id not in tracks_id and tracks[number].id not in repeats:
                tracks_id.append(tracks[number].id)
                tracks_list.append(tracks[number])

        self.logger.info(f"{len(tracks_list)} Треков отобрано")
        return tracks_list

    def snippet_from_track(self, track: bytes, length_ms: int) -> bytes:
        """
        Делает сниппет из указанного трека в виде байтов

        :param track: Трек на обрезание
        :type track: bytes
        :param length_ms: Длина отрезка
        :type length_ms: int
        :return: Обрезанный фрагмент в виде байтов
        :rtype: bytes
        """

        audio_buffer = BytesIO(track)
        audio = AudioSegment.from_file(audio_buffer)

        max_start = max(0, len(audio) - length_ms)

        start_time = randint(0, max_start)
        end_time = start_time + length_ms
        audio_snippet = audio[start_time:end_time]

        output_buffer = BytesIO()
        audio_snippet.export(output_buffer, format="mp3")

        return output_buffer.getvalue()

    # Асинхронные варианты

    @rotate_proxy_async
    async def get_track_by_id_async(
        self, track_ids: List[str | int] | int | str
    ) -> List[Track]:
        """
        Асинхронно возвращает список объектов Track по их id

        :param track_ids: id треков
        :type track_ids: List[str | int] | int | str
        :return: Список с полученными треками
        :rtype: List[Track]
        """
        await self._ensure_async_client()

        tracks = await self.clientAsync.tracks(track_ids)
        self.logger.info(f"{len(tracks)} треков найдено")
        return tracks

    @rotate_proxy_async
    async def get_bytes_async(self, track: Track, bitrate_in_kbps: int = 192) -> bytes:
        """
        Асинхронно возвращает объект Track в виде байтов

        :param track: Трек для преобразования
        :type track: Track
        :param bitrate_in_kbps: Возможные значения: `64`, `128`, `192`, `320`.
        :type bitrate_in_kbps: int
        :return: Трек в виде байтов
        :rtype: bytes
        """
        await self._ensure_async_client()
        try:
            self.logger.info(
                f"Скачиваем трек {track.title} с битрейтом {bitrate_in_kbps}"
            )
            return await track.download_bytes_async(bitrate_in_kbps=bitrate_in_kbps)

        except InvalidBitrateError:
            self.logger.info(
                f"Ошибка скачивания {track.title} с битрейтом {bitrate_in_kbps} скачиваем с битрейтом 192"
            )
            return await track.download_bytes_async(bitrate_in_kbps=192)

    @rotate_proxy_async
    async def search_artist_async(self, artist_name: str) -> Optional[List[Artist]]:
        """
        Асинхронно возвращает список найденных артистов

        :param input: Имя артиста
        :type input: str
        :return: Список артистов
        :rtype: List[Artist] | None
        """

        await self._ensure_async_client()
        search = await self.clientAsync.search(artist_name, type_="artist")

        if not search or not search.artists:
            return None

        self.logger.info(f"Найдены следующие артисты {search.artists.results}")
        return search.artists.results

    @rotate_proxy_async
    async def get_tracks_from_artist_async(
        self, artist: Artist, tracks_count: int = 200
    ) -> Optional[List[Track]]:
        """
        Асинхронно получает треки у объекта `artist`

        :param artist: Артист с которого будут получены треки
        :type artist: Artist
        :param tracks_count: Кол-во получаемых треков по умолчанию: `20`
        :type tracks_count: int
        :return: Список треков
        :rtype: List[Track] | None
        """

        await self._ensure_async_client()
        artistTracks = await artist.get_tracks_async(page_size=tracks_count)

        if not artistTracks:
            return None

        self.logger.info(f"Найдены следующие треки: {artistTracks.tracks}")

        return artistTracks.tracks
