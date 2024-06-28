from __future__ import annotations
from typing import TYPE_CHECKING
from enum import Enum

import os

from managers.logger_manager import LoggerManager
from utils.log_message import LogMessage
from utils.log_storage import log_store

if TYPE_CHECKING:
    import obj.worldobj.entity

class LogLevel(Enum):
    INFO = 1
    WARN = 2
    ERROR = 3
    FATAL = 4
    DEBUG = 5

class Logger:
    def __init__(self, name: str, manager: LoggerManager):
        self.name = name
        self.messages = {}
        self.log_store = log_store
        manager.loggers[name] = self
    
    def log(self, log_level, message: str, *args, actor: obj.worldobj.entity.Entity = None):
        log_message = LogMessage(self.name, message, log_level, *args, actor=actor)
        
        self.log_store.add_message(log_message)
        
        # self.messages[log_level].append(log_message)
        
        # print(log_message)
        
        if len(self.log_store.get_messages()) > 25:
            self.log_store.flush_messages()
    
    def info(self, message: str, *args, actor=None):
        self.log(LogLevel.INFO, message, *args, actor=actor)
    
    def warn(self, message: str, *args, actor=None):
        self.log(LogLevel.WARN, message, *args, actor=actor)
    
    def error(self, message: str, *args, actor=None):
        self.log(LogLevel.ERROR, message, *args, actor=actor)
    
    def fatal(self, message: str, *args, actor=None):
        self.log(LogLevel.FATAL, message, *args, actor=actor)
    
    def debug(self, message: str, *args, actor=None):
        self.log(LogLevel.DEBUG, message, *args, actor=actor)
    
    def flush_messages(self):
        if not os.path.exists("logs"):
            os.mkdir("logs")
        
        # Write to general logfile and individual logfiles
        with open("logs/all.log", "a") as f:
            for messages in self.messages.values():
                for message in messages:
                    f.write(str(message) + "\n")
        
        with open(f"logs/{self.name}.log", "a") as f:
            for messages in self.messages.values():
                for message in messages:
                    f.write(str(message) + "\n")
        
        for log_level in self.messages:
            with open(f"logs/{str(log_level).split('.')[1]}.log", "a") as f:
                for message in self.messages[log_level]:
                    f.write(str(message) + "\n")
                self.messages[log_level] = []
        
            with open(f"logs/{self.name}_{str(log_level).split('.')[1]}.log", "a") as f:
                for message in self.messages:
                    f.write(str(message) + "\n")
                self.messages[log_level] = []