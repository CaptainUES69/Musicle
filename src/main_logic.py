from io import BytesIO
from logging import Logger
from typing import Dict, List

from .audio import AudioFile
from .conf import CustomLogger


class MainLogic:
    audio: AudioFile
    logger: Logger = CustomLogger("main_logic")._logger

    # Внутренние методы

    def __init__(self):
        self.audio = AudioFile()

    # Основная логика

    def metadata(
        self, artist_name: str, rounds: int, length_ms: int, repeats: set[int | str]
    ) -> List[Dict[str, str | list[str]]]:
        """Получение треков с их метаданными

        :param artist_name: Имя исполнителя
        :type artist_name: str
        :param rounds: Кол-во треков
        :type rounds: int
        :param length_ms: Длина треков в подборке
        :type length_ms: int
        :param repeats: список с ID треков которые надо отсеять, по умолчанию равно None
        :type repeats: set[int  |  str], optional
        :return: Список с метаданными треков
        :rtype: List[Dict[str, str | list[str]]]
        """
        artist = self.audio.search_artist(artist_name)
        tracks = self.audio.get_tracks_from_artist(artist[0])
        track_list = self.audio.choose_tracks(tracks, rounds, repeats)

        forward_data: list[dict] = []
        for track in track_list:
            forward_data.append(
                {
                    "title": track.title,
                    "artist": [name for name in track.artists_name()],
                    "snippet_url": f"/snippet/{track.id}?length_ms={length_ms}",
                    "track_id": track.id,
                }
            )

        return forward_data

    def trim_track(self, track_id: str | int, length_ms: int) -> BytesIO:
        """Обрезает треки

        :param track_id: ID трека
        :type track_id: str | int
        :param length_ms: Длина трека в миллисекундах
        :type length_ms: int
        :return: Байтовое представление трека
        :rtype: BytesIO
        """
        track = self.audio.get_track_by_id(track_id)
        track_bytes = self.audio.get_bytes(track[0])

        return BytesIO(self.audio.snippet_from_track(track_bytes, length_ms))

    # Асинхронные варианты

    async def metadata_async(
        self,
        artist_name: str,
        rounds: int,
        length_ms: int,
        repeats: set[int | str] = None,
    ) -> List[Dict[str, str | list[str]]]:
        """Асинхронное получение треков с их метаданными

        :param artist_name: Имя исполнителя
        :type artist_name: str
        :param rounds: Кол-во треков
        :type rounds: int
        :param length_ms: Длина треков в подборке
        :type length_ms: int
        :param repeats: список с ID треков которые надо отсеять, по умолчанию равно None
        :type repeats: set[int  |  str], optional
        :return: Список с метаданными треков
        :rtype: List[Dict[str, str | list[str]]]
        """
        artist = await self.audio.search_artist_async(artist_name)
        tracks = await self.audio.get_tracks_from_artist_async(artist[0])
        track_list = self.audio.choose_tracks(tracks, rounds, repeats)

        forward_data: List[Dict[str, str | list[str]]] = []
        for track in track_list:
            forward_data.append(
                {
                    "title": track.title,
                    "artist": [name for name in track.artists_name()],
                    "snippet_url": f"/snippet/{track.id}?length_ms={length_ms}",
                    "track_id": track.id,
                }
            )

        return forward_data

    async def trim_track_async(self, track_id: str | int, length_ms: int) -> BytesIO:
        """Асинхронно обрезает треки

        :param track_id: ID трека
        :type track_id: str | int
        :param length_ms: Длина трека в миллисекундах
        :type length_ms: int
        :return: Байтовое представление трека
        :rtype: BytesIO
        """
        track = await self.audio.get_track_by_id_async(track_id)
        track_bytes = await self.audio.get_bytes_async(track[0])

        return BytesIO(self.audio.snippet_from_track(track_bytes, length_ms))
