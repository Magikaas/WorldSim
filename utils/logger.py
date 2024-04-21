from __future__ import annotations
from typing import TYPE_CHECKING
from enum import Enum

import os

if TYPE_CHECKING:
    import obj.worldobj.entity

class LogLevel(Enum):
    INFO = 1
    WARN = 2
    ERROR = 3
    FATAL = 4
    DEBUG = 5

class Logger:
    def __init__(self, name: str):
        self.name = name
    
    def log(self, log_level, message: str, *args, actor: obj.worldobj.entity.Entity = None):
        level = str(log_level).ljust(15)
        prefix = self.name.ljust(20)
        
        actor_name = actor.name if actor else "General"
        
        actor_name = actor_name.ljust(10)
        
        log_message = f"[{actor_name}] [{level}] [{prefix}] {message}" + (" " if len(args) > 0 else "") + ' '.join([str(i) for i in args])
        
        # print(log_message)
        
        if not os.path.exists("logs"):
            os.mkdir("logs")
        
        # Write to general logfile and individual logfiles
        with open("logs/all.log", "a") as f:
            f.write(log_message + "\n")
        
        with open(f"logs/{str(log_level).split('.')[1]}.log", "a") as f:
            f.write(log_message + "\n")
        
        with open(f"logs/{self.name}.log", "a") as f:
            f.write(log_message + "\n")
        
        with open(f"logs/{self.name}_{str(log_level).split('.')[1]}.log", "a") as f:
            f.write(log_message + "\n")
    
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