import logging

from dotenv import load_dotenv
from yandex_music import Client
from os import getenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    filename="py_log.log",
    filemode="w",
    encoding="utf-8",
    format="%(asctime)s %(levelname)s -- %(funcName)s(%(lineno)d) - %(message)s"
)


client = Client(token=getenv("YANDEX_TOKEN"))
