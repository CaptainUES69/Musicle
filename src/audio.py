from io import BytesIO
from os import getenv
from random import randint
from typing import List, Optional

from dotenv import load_dotenv
from pydub import AudioSegment
from yandex_music import Client, ClientAsync
from yandex_music.artist.artist import Artist
from yandex_music.exceptions import InvalidBitrateError
from yandex_music.track.track import Track


class AudioFile:
    '''
    Класс для работы с YandexMusicApi и полученными аудиофайлами
    '''
    client: Client
    clientAsync: ClientAsync = None

    def __init__(self):
        load_dotenv(override=True)
        self.client = Client(getenv('YANDEX_TOKEN')).init()

    
    async def _ensure_async_client(self):
        if self.clientAsync is None:
            self.clientAsync = ClientAsync(getenv('YANDEX_TOKEN'))
            await self.clientAsync.init()
    

    def get_track_by_id(self, track_ids: List[str | int] | int | str) -> List[Track]:
        '''
        Возвращает список объектов Track по их id
        
        :param track_ids: id треков
        :type track_ids: List[str | int] | int | str
        :return: Список с полученными треками
        :rtype: List[Track]
        '''

        tracks = self.client.tracks(track_ids)
        return tracks
    

    async def get_track_by_id_async(self, track_ids: List[str | int] | int | str) -> List[Track]:
        '''
        Асинхронно возвращает список объектов Track по их id
        
        :param track_ids: id треков
        :type track_ids: List[str | int] | int | str
        :return: Список с полученными треками
        :rtype: List[Track]
        '''
        await self._ensure_async_client()

        tracks = await self.clientAsync.tracks(track_ids)
        return tracks


    def get_bytes(self, track: Track, bitrate_in_kbps: int = 192) -> bytes:
        '''
        Возвращает объект Track в виде байтов
        
        :param track: Трек для преобразования
        :type track: Track
        :param bitrate_in_kbps: Возможные значения: `64`, `128`, `192`, `320`.
        :type bitrate_in_kbps: int
        :return: Трек в виде байтов
        :rtype: bytes
        '''
        try:
            return track.download_bytes(bitrate_in_kbps = bitrate_in_kbps)
        
        except InvalidBitrateError:
            return track.download_bytes(bitrate_in_kbps = 192)
    

    async def get_bytes_async(self, track: Track, bitrate_in_kbps: int = 192) -> bytes:
        '''
        Асинхронно возвращает объект Track в виде байтов
        
        :param track: Трек для преобразования
        :type track: Track
        :param bitrate_in_kbps: Возможные значения: `64`, `128`, `192`, `320`.
        :type bitrate_in_kbps: int
        :return: Трек в виде байтов
        :rtype: bytes
        '''
        try:
            return await track.download_bytes_async(bitrate_in_kbps = bitrate_in_kbps)
        
        except InvalidBitrateError:
            return await track.download_bytes_async(bitrate_in_kbps = 192)


    def search_tracks(self, input: str) -> Optional[List[Track]]:
        '''
        Возвращает список объектов Track после поиска по названию
        
        :param input: Текст для поиска
        :type input: str
        :return: Список найденных треков
        :rtype: List[Track] | None
        '''

        search = self.client.search(input, type_='track')
        
        if not search or not search.tracks:
            return None
        
        return search.tracks.results


    def search_artist(self, artist_name: str) -> Optional[List[Artist]]:
        '''
        Возвращает список найденных артистов
        
        :param input: Имя артиста
        :type input: str
        :return: Список артистов
        :rtype: List[Artist] | None
        '''
        
        search = self.client.search(artist_name, type_='artist')

        if not search or not search.artists:            
            return None

        return search.artists.results
    

    async def search_artist_async(self, artist_name: str) -> Optional[List[Artist]]:
        '''
        Асинхронно возвращает список найденных артистов
        
        :param input: Имя артиста
        :type input: str
        :return: Список артистов
        :rtype: List[Artist] | None
        '''
        
        await self._ensure_async_client()
        search = await self.clientAsync.search(artist_name, type_='artist')

        if not search or not search.artists:            
            return None

        return search.artists.results


    def get_tracks_from_artist(self, artist: Artist, tracks_count: int = 20) -> Optional[List[Track]]:
        '''
        Получает треки у объекта `artist`
        
        :param artist: Артист с которого будут получены треки
        :type artist: Artist
        :param tracks_count: Кол-во получаемых треков по умолчанию: `20`
        :type tracks_count: int
        :return: Список треков
        :rtype: List[Track] | None
        '''
        
        artistTracks = artist.getTracks(page_size = tracks_count)

        if not artistTracks:
            return None
        
        return artistTracks.tracks


    async def get_tracks_from_artist_async(self, artist: Artist, tracks_count: int = 20) -> Optional[List[Track]]:
        '''
        Асинхронно получает треки у объекта `artist`
        
        :param artist: Артист с которого будут получены треки
        :type artist: Artist
        :param tracks_count: Кол-во получаемых треков по умолчанию: `20`
        :type tracks_count: int
        :return: Список треков
        :rtype: List[Track] | None
        '''
        
        await self._ensure_async_client()
        artistTracks = await artist.get_tracks_async(page_size = tracks_count) 

        if not artistTracks:
            return None
        
        return artistTracks.tracks
    

    def choose_tracks(self, tracks: list[Track], count: int) -> List[Track]:
        '''
        Выбирает треки из Листа с ними без повторений
        
        :param tracks: Список всех треков из которых выбирается `count` кол-во треков
        :type tracks: list[Track]
        :param count: Количество нужных треков
        :type count: int
        :return: Лист уникальных треков
        :rtype: List[Track]
        '''

        tracks_id: list[str | int] = []
        tracks_list: list[Track] = []

        while len(tracks_list) < count:
            number = randint(0, len(tracks)-1)

            if tracks[number].id not in tracks_id:
                tracks_id.append(tracks[number].id)
                tracks_list.append(tracks[number])

        return tracks_list


    def snippet_from_track(self, track: bytes, length_ms: int) -> bytes:
        '''
        Делает сниппет из указанного трека в виде байтов
        
        :param track: Трек на обрезание
        :type track: bytes
        :param length_ms: Длина отрезка
        :type length_ms: int
        :return: Обрезанный фрагмент в виде байтов
        :rtype: bytes
        '''

        audio_buffer = BytesIO(track)
        audio = AudioSegment.from_file(audio_buffer)

        max_start = max(0, len(audio) - length_ms)

        start_time = randint(0, max_start)
        end_time = start_time + length_ms
        audio_snippet = audio[start_time:end_time]

        output_buffer = BytesIO()
        audio_snippet.export(output_buffer, format="mp3")
        
        return output_buffer.getvalue()