import json
import logging
import os
from logging.handlers import RotatingFileHandler


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        return json.dumps(log_record)


class LoggerFactory:
    _configured = False

    @classmethod
    def _configure(cls):
        if cls._configured:
            return

        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        log_format = os.getenv("LOG_FORMAT", "text").lower()
        log_file = os.getenv("LOG_FILE", "logs/worker.log")

        if log_format == "json":
            formatter = JsonFormatter()
        else:
            formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
            )

        file_handler = RotatingFileHandler(
            log_file, maxBytes=2 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        logging.basicConfig(
            level=log_level, handlers=[file_handler, console_handler], force=True
        )

        cls._configured = True

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        cls._configure()
        return logging.getLogger(name)
