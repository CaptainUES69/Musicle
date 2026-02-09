from src.music_api import AudioFile
from src.audio_processing import AudioProccesing


audio = AudioFile()
proccessing = AudioProccesing()

artists = audio.search_artist(input('Введите имя артиста: '))

art = int(input('Введите номер нужного артиста: '))
number = int(input('Введите кол-во нужных треков: '))
tracks = audio.get_track_from_artist(artists[art], tracks_count = number)

num = int(input('Введите кол-во нужных треков: '))
choosed_tracks = proccessing.choose_tracks(tracks, num)

audio_bytes: list[bytes] = []
for track in choosed_tracks:
    audio_bytes.append(audio.get_bytes(track))

