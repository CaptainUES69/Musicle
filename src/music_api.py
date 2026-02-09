from os import getenv
from typing import List, Optional

from dotenv import load_dotenv
from yandex_music import Client
from yandex_music.artist.artist import Artist
from yandex_music.track.track import Track


class AudioFile:
    client: Client

    def __init__(self):
        load_dotenv(override=True)
        self.client = Client(getenv('YANDEX_TOKEN')).init()
    

    def get(self, track_ids: List[str | int] | int | str) -> List[Track]:
        '''
        Возвращает список объектов Track по их id
        
        :param track_ids: id треков
        :type track_ids: List[str | int] | int | str
        :return: Список с полученными треками
        :rtype: List[Track]
        '''

        tracks = self.client.tracks(track_ids)
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

        return track.download_bytes(bitrate_in_kbps = bitrate_in_kbps)


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


    def search_artist(self, input: str) -> Optional[List[Artist]]:
        '''
        Возвращает список найденных артистов
        
        :param input: Имя артиста
        :type input: str
        :return: Список артистов
        :rtype: List[Artist] | None
        '''
        
        search = self.client.search(input, type_='artist')

        if not search or not search.artists:            
            return None

        return search.artists.results


    def get_track_from_artist(self, artist: Artist, tracks_count: int = 20) -> List[Track]:
        '''
        Получает треки у объекта `artist`
        
        :param artist: Артист с которого будут получены треки
        :type artist: Artist
        :param tracks_count: Кол-во получаемых треков по умолчанию `20`
        :type tracks_count: int
        :return: Список треков
        :rtype: List[Track]
        '''

        artistTracks = artist.getTracks(page_size = tracks_count)
        return artistTracks.tracks
