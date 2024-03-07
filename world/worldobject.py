from enum import Enum

class WORLD_OBJECT_TYPE(Enum):
    ITEM = 0
    CONTAINER = 1
    BUILDING = 2
    ANIMAL = 3
    RESOURCE = 4
    RESOURCE_NODE = 5

class WorldObject:
    def __init__(self, name, description, object_type: WORLD_OBJECT_TYPE):
        self.name = name
        self.description = description
        self.object_type = object_type