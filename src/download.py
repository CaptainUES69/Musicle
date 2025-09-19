from utility import process_track, extract_artist_id
import random

from cfg import logging, client


def download_by_search_track(search_data: str, trim_duration: int = 10) -> None:
    """Скачивание по поиску трека"""
    try:
        find = client.search(search_data, type_="track")
        if not find.tracks or not find.tracks.results:
            logging.error("Треки не найдены")
        
        track = find.tracks.results[0]
        process_track(track, trim_duration)

    except Exception as e:
        logging.error(f"Ошибка в download_by_search_track: {e}", exc_info=True)

def download_by_name_artist(search_data: str, trim_duration: int = 10) -> None:
    """Скачивание по имени исполнителя"""
    try:
        find = client.search(search_data, type_="artist").artists
        if not find or not find.results:
            logging.error("Исполнитель не найден")

        artist = find.results[0]
        artist_tracks = client.artists_tracks(artist.id)
        if not artist_tracks or not artist_tracks.tracks:
            logging.error("Треки не найдены")
        
        track = artist_tracks.tracks[random.randint(0, len(artist_tracks.tracks) - 1)]
        process_track(track, trim_duration)

    except Exception as e:
        logging.error(f"Ошибка в download_by_name_artist: {e}", exc_info=True)

def download_by_url_artist(search_data: str, trim_duration: int = 10) -> None:
    """Скачивание по URL исполнителя"""
    try:
        artist_id = extract_artist_id(search_data)
        if not artist_id:
            logging.error("ID не найден")
       
        find = client.artists_tracks(artist_id)
        if not find or not find.tracks:
            logging.error("Исполнитель не найден")

        track = find.tracks[random.randint(0, len(find.tracks) - 1)]
        process_track(track, trim_duration)
        
    except Exception as e:
        logging.error(f"Ошибка в download_by_url_artist: {e}", exc_info=True)
