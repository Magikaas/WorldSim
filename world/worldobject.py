from dataclasses import dataclass
from enum import Enum
from typing import Protocol

class WORLD_OBJECT_TYPE(Enum):
    ITEM = 0
    CONTAINER = 1
    BUILDING = 2
    ANIMAL = 3
    RESOURCE = 4
    RESOURCE_NODE = 5

@dataclass
class WorldObject(Protocol):
    name: str
    description: str