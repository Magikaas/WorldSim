from enum import IntEnum

class MapRenderType(IntEnum):
    """Enum to determine the type of map rendering."""
    ALL = 31
    PATHFINDING = 16
    ANIMALS = 8
    POPS = 4
    RESOURCES = 2
    TERRAIN = 1