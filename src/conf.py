from logging import INFO, Formatter, getLogger
from logging.handlers import RotatingFileHandler

# Настройки логгирования
logger = getLogger("App")
logger.level = INFO  # Уровень логирования

handler = RotatingFileHandler(
    filename = "app.log", maxBytes = (5 * 1024 * 1024), backupCount = 5, encoding = "utf-8"
)

formatter = Formatter(
    "%(asctime)s %(levelname)s -- %(funcName)s(%(lineno)d) - %(message)s"
)
handler.setFormatter(formatter)

logger.addHandler(handler)