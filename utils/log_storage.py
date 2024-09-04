# Class for keeping all logs in memory, and flushing them to disk when needed
from dataclasses import dataclass, field

import os

@dataclass
class LogStore:
    messages: list = field(default_factory=list)
    
    def add_message(self, message):
        self.messages.append(message)
    
    def get_messages(self):
        return self.messages
    
    def flush_messages(self):
        if not os.path.exists("logs"):
            os.mkdir("logs")
        
        log_levels = []
        
        for message in self.messages:
            if message.level not in log_levels:
                log_levels.append(message.level)
        
        # Write to general logfile and individual logfiles
        with open("logs/all.log", "a") as f:
            for message in self.messages:
                f.write(str(message) + "\n")
        
        for log_level in log_levels:
            with open(f"logs/{str(log_level).split('.')[1]}.log", "a") as f:
                for message in self.messages:
                    if message.level == log_level:
                        f.write(str(message) + "\n")
        
        self.messages = []

# Singleton class for storing logs
log_store = LogStore()