from dataclasses import dataclass, field

@dataclass
class LoggerManager:
    loggers: dict = field(default_factory=dict)

logger_manager = LoggerManager()