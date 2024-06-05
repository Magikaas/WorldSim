from __future__ import annotations
from typing import TYPE_CHECKING
from enum import Enum

import os

from managers.logger_manager import LoggerManager
from utils.log_message import LogMessage

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
        manager.loggers[name] = self
    
    def log(self, log_level, message: str, *args, actor: obj.worldobj.entity.Entity = None):
        prefix = self.name.ljust(20)
        
        log_message = LogMessage(prefix, message, log_level, *args, actor=actor)
        
        if log_level not in self.messages:
            self.messages[log_level] = []
        
        self.messages[log_level].append(log_message)
        
        if actor is not None:
            actor_name = actor.name
        else:
            actor_name = "None"
        
        level = str(log_level).split('.')[1]
        
        log_message = f"[{actor_name}] [{level}] [{prefix}] {message}" + (" " if len(args) > 0 else "") + ' '.join([str(i) for i in args])
        
        # print(log_message)
        
        for log_level in self.messages:
            if len(self.messages[log_level]) > 25:
                self.flush_messages()
    
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
        
        self.messages = {}