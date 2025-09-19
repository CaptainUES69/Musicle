from fastapi import FastAPI

import uvicorn
import asyncio

from cfg import logging

from download import download_by_name_artist, download_by_url_artist


app = FastAPI()

@app.get("/")
async def main_page():
    
    
    ...

async def main():
    download_by_name_artist(input("Имя Уолтер: "))
    # uvicorn.run(app, host = "127.0.0.1", port = 8000)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"Ошибка при обрабокте запросов: {e}", exc_info=True)