from io import BytesIO
from random import randint
from typing import List, Optional

from pydub import AudioSegment
from yandex_music.artist.artist import Artist
from yandex_music.track.track import Track

# from src.music_api import AudioFile


class AudioProccesing:
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


    def snippet_from_track(self, track: bytes, snippet_length_ms: int) -> bytes:
        '''
        Делает сниппет из указанного трека в виде байтов
        
        :param track: Трек на обрезание
        :type track: bytes
        :param snippet_length_ms: Длина отрезка
        :type snippet_length_ms: int
        :return: Обрезанный фрагмент в виде байтов
        :rtype: bytes
        '''

        audio_buffer = BytesIO(track)
        audio = AudioSegment.from_file(audio_buffer)

        max_start = max(0, len(audio) - snippet_length_ms)

        start_time = randint(0, max_start)
        end_time = start_time + snippet_length_ms
        audio_snippet = audio[start_time:end_time]

        output_buffer = BytesIO()
        audio_snippet.export(output_buffer, format="mp3")
        
        return output_buffer.getvalue()
    