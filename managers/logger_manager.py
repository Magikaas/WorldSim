from dataclasses import dataclass


@dataclass
class LoggerManager:
    loggers = {}

logger_manager = LoggerManager()