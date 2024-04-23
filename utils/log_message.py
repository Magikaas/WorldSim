from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import obj.worldobj.entity

class LogMessage:
    def __init__(self, prefix: str, message: str, level: str, *args, actor: obj.worldobj.entity.Entity = None):
        self.prefix = prefix
        self.message = message
        self.level = level
        self.args = args
        self.actor = actor

    def __str__(self):
        level = str(self.level).ljust(15)
        prefix = self.prefix
        
        actor_name = self.actor.name if self.actor else "General"
        
        actor_name = actor_name.ljust(10)
        
        return f"[{actor_name}] [{level}] [{prefix}] {self.message}" + (" " if len(self.args) > 0 else "") + ' '.join([str(i) for i in self.args])