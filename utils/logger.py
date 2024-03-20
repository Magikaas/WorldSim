from enum import Enum

class LogLevel(Enum):
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3
    FATAL = 4

class Logger:
    def __init__(self, name: str, level: LogLevel = LogLevel.INFO):
        self.name = name
        self.level = level
    
    def log(self, message: str, *args):
        prefix = self.name.ljust(15)
        print(f"[{prefix}] {message}", *args)
    
    def debug(self, message: str, *args):
        if self.level.value <= LogLevel.DEBUG.value:
            self.log(message, *args)
    
    def info(self, message: str, *args):
        if self.level.value <= LogLevel.INFO.value:
            self.log(message, *args)
    
    def warn(self, message: str, *args):
        if self.level.value <= LogLevel.WARN.value:
            self.log(message, *args)
    
    def error(self, message: str, *args):
        if self.level.value <= LogLevel.ERROR.value:
            self.log(message, *args)
    
    def fatal(self, message: str, *args):
        if self.level.value <= LogLevel.FATAL.value:
            self.log(message, *args)
    
    def set_level(self, level: LogLevel):
        self.level = level