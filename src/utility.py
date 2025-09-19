from pydub import AudioSegment
import random
import re

from cfg import logging

from yandex_music.exceptions import InvalidBitrateError
from yandex_music.track.track import Track


def extract_artist_id(url: str) -> str | None:
    """Ищет ID артиста в ссылке на него"""
    try:
        pattern = r"/artist/(\d+)"
        match = re.search(pattern, url)
        if match:
            logging.info(f"Совпадения обнаружены {match=}")
            return match.group(1)
        
        logging.info(f"Совпадений не найдено {match=}")
        return None
    
    except Exception as e:
        logging.info(f"Ошибка в в extract_artist_id: {e}", exc_info=True)
        return None

def trim_random_segment(path: str, duration_seconds: int = 10) -> None:
    """Обрезает аудиофайл и перезаписывает его"""
    try:
        audio = AudioSegment.from_mp3(path)
        total_ms = len(audio)
        duration_ms = duration_seconds * 1000
        
        if total_ms <= duration_ms:
            logging.warning(f"Трек слишком короткий ({total_ms/1000:.1f}с). Возвращаем оригинал.")
            return None
        
        max_start = total_ms - duration_ms
        start_time = random.randint(0, max_start)
        
        clip = audio[start_time:start_time + duration_ms]
        clip.export(path, format="mp3")
        
        logging.info(f"Создан клип: {path} (начало: {start_time/1000:.1f}с)")
        return None
        
    except Exception as e:
        logging.error(f"Ошибка при обрезке файла {path}: {e}", exc_info=True)
        return None

def download_track(track: Track, filename: str) -> bool:
    """Универсальная функция для скачивания трека с обработкой разных битрейтов"""
    try:
        download_info = track.get_download_info()
        
        if download_info:
            kbps = download_info[0].bitrate_in_kbps
            track.download(filename, bitrate_in_kbps=kbps)
            logging.debug(f"Скачан с битрейтом {kbps}: {filename}")
            return True
        
    except InvalidBitrateError:
        bitrates = [320, 192, 128, 64]
        for bitrate in bitrates:
            try:
                track.download(filename, bitrate_in_kbps=bitrate)
                logging.debug(f"Скачан с битрейтом {bitrate}: {filename}")
                return True
            
            except InvalidBitrateError:
                logging.debug(f"Битрейт {bitrate} недоступен")
                continue
        logging.error("Не удалось скачать трек с любым из битрейтов")
    
    except Exception as e:
        logging.error(f"Неизвестная ошибка: {e}", exc_info=True)

    return False

def process_track(track: Track, trim_duration: int) -> None:
    """Обработка трека: скачивание и обрезка"""
    artists = ", ".join(track.artists_name())
    logging.debug(f'{track.id} {artists} - {track.title}')
    filename = f"{artists} - {track.title}.mp3"
    
    if not download_track(track, filename):
        return False
    
    trim_random_segment(filename, trim_duration)
    logging.info(f"Успешно создан обрезанный файл: {filename}")
