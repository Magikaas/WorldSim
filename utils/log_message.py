from __future__ import annotations
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import obj.worldobj.entity

class LogMessage:
    def __init__(self, name: str, message: str, level: str, *args, actor: obj.worldobj.entity.Entity = None):
        self.name = name
        self.message = message
        self.level = level
        self.args = args
        self.actor = actor

    def __str__(self):
        level = str(self.level).ljust(14)
        prefix = prefix = self.name.ljust(25)
        
        actor_name = self.actor.name if self.actor else "General"
        
        actor_name = actor_name.ljust(8)
        
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        
        # Make sure timestamp is always 19 characters long
        timestamp = timestamp.ljust(19)
        
        return f"[{timestamp}][{actor_name}] [{level}] [{prefix}] {self.message}" + (" " if len(self.args) > 0 else "") + ' '.join([str(i) for i in self.args])