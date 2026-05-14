# Musicle
## О проекте

Веб-приложение, которое представляет собой музыкальный квиз.

*Все треки взяты из Яндекс музыки и не используются в коммерческих целях*

## Технологии

| Слой | Стек |
|------|------|
| Фронтенд | HTML5, CSS3, JavaScript Vanilla (ES6+) |
| Бэкенд | Python 3.12+, FastAPI, SQLAlchemy 2 |
| СУБД | SQLite (Временное решение в виду малого объема записываеммых данных) |
| Сервер | gunicorn (в Docker) или uvicorn dev-сервер |
| Деплой | Docker Compose (FASTAPI + SQLite) |

## Структура проекта

```
Musicle/
├── .env.example               — образец переменных окружения (YANDEX_TOKEN и др.)
├── .gitignore
├── .dockerignore
├── docker-compose.yml         — оркестрация backend + nginx + томов
├── Dockerfile                 — основной образ Python с ffmpeg
├── requirements.txt           — зависимости Python (FastAPI, uvicorn, aiohttp и пр.)
├── README.md
│
├── backend/                   — Python/FastAPI (в репозитории называется src/)
│   ├── main.py                — точка входа: создание FastAPI, CORS, запуск Uvicorn
│   ├── conf.py                — настройка логгера с RotatingFileHandler
│   ├── utils.py               — вспомогательные константы и список сайтов для CORS
│   ├── methods.py             — бизнес-логика викторины (обработка ответов и т.д.)
│   ├── audio.py               — работа с аудио через ffmpeg (обрезка треков)
│   ├── api/                   — роутеры HTTP-запросов
│   │   ├── tracks.py          — эндпоинты музыкальной викторины
│   │   └── leaderboard.py     — эндпоинты таблицы лидеров
│   └── database/              — работа с SQLite через SQLAlchemy
│       ├── core.py            — создание сессии и инициализация БД
│       ├── models.py          — модели данных (DDL описаны здесь, аналог schema.sql)
│       └── methods.py         — функции взаимодействия с БД
│
├── frontend/                  — статический фронтенд
│   ├── index.html             — разметка страниц
│   ├── style.css              — стили
│   └── script.js              — логика викторины, запросы к API
│
└── nginx/                     — кастомный образ Nginx
    ├── Dockerfile             — сборка образа Nginx с конфигом
    └── nginx.conf             — маршрутизация: статика напрямую, API на backend
```

## Быстрый запуск через Docker 
```bash
git pull https://github.com/CaptainUES69/Musicle.git
docker-compose build
docker-compose up
```

## Маршруты

### Публичные страницы

| Путь | Описание |
|------|----------|
| `/` | Главная |

### REST API
| Метод | Путь | Назначение |
|-------|------|------------|
| `GET/POST` | `/api/tracks/get_tracks/<artist_name>` | Получение метаданных треков |
| `GET` | `/api/tracks/snippet/<track_id>` | Получение аудио |
| `POST` | `/api/leaderboard/user` | Создание/обновление данных в бд |
| `GET` | `/api//leaderboard/top` | Получение топа игроков |
| `GET` | `/api//leaderboard/top_artist/<artist_name>` | Получение топа игроков по артисту |







