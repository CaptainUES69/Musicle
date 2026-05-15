from logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    INFO,
    WARNING,
    Formatter,
    Logger,
    getLogger,
    StreamHandler,
)
from logging.handlers import RotatingFileHandler
from os import makedirs, path
from sys import stdout


class CustomLogger:
    _logger: Logger

    def __init__(
        self,
        filename: str,
        loggerName: str = None,
        level: int = WARNING,
        backupCount: int = 5,
        formatter: Formatter = Formatter(
            "%(asctime)s %(levelname)s -- %(funcName)s(%(lineno)d) - %(message)s"
        ),
        debugMode: bool = False,
    ) -> Logger:
        """_summary_

        Args:
            filename (str): Название файла
            loggerName (str, optional): Название логгера. По умолчанию равно имени файла.
            level (int, optional): Уровень логирования по системе logging. По умолчанию равно INFO.
            backupCount (int, optional): Количество бекапов файлов. По умолчанию равно 5 файлам.
            formatter (Formatter, optional): Формат логов, по умолчанию Formatter("%(asctime)s %(levelname)s -- %(funcName)s(%(lineno)d) - %(message)s").
        """
        if not loggerName:
            loggerName = filename
        self._logger = getLogger(loggerName)
        self._logger.level = level
        self._logger.propagate = False

        if debugMode:
            if not path.exists(f"logs"):
                makedirs(f"logs", exist_ok=True)

            file_handler = RotatingFileHandler(
                filename=f"logs/{filename}.log",
                maxBytes=(5 * 1024 * 1024),
                backupCount=backupCount,
                encoding="utf-8",
            )
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)

            console_handler = StreamHandler(stdout)
            console_handler.setFormatter(formatter)
            self._logger.addHandler(console_handler)

        else:
            handler = StreamHandler(stdout)
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
