from dataclasses import dataclass, field

@dataclass
class LoggerManager:
    loggers: dict = field(default_factory=dict)
    sim_step: int = 0

logger_manager = LoggerManager()