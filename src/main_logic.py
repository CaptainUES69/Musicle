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
    ) -> List[Dict]:
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
                }
            )

        return forward_data

    def trim_track(self, track_id: str | int, length_ms: int) -> BytesIO:
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
    ) -> List[Dict]:
        artist = await self.audio.search_artist_async(artist_name)
        tracks = await self.audio.get_tracks_from_artist_async(artist[0])
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

    async def trim_track_async(self, track_id: str | int, length_ms: int) -> BytesIO:
        track = await self.audio.get_track_by_id_async(track_id)
        track_bytes = await self.audio.get_bytes_async(track[0])

        return BytesIO(self.audio.snippet_from_track(track_bytes, length_ms))
