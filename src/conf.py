from logging import INFO, Formatter, getLogger, Logger
from logging.handlers import RotatingFileHandler



class Logging:
    logger: Logger

    def __init__(
            self,
            filename: str,
            loggerName: str     
        ):
        self.logger = getLogger(loggerName)
        self.logger.level = INFO

        handler = RotatingFileHandler(
            filename = filename, 
            maxBytes = (5 * 1024 * 1024), 
            backupCount = 5, 
            encoding = 'utf-8'
        )
        formatter = Formatter("%(asctime)s %(levelname)s -- %(funcName)s(%(lineno)d) - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
