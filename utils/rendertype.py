from enum import IntEnum

class MapRenderType(IntEnum):
    """Enum to determine the type of map rendering."""
    ALL = 63
    PATHFINDING = 32
    ANIMALS = 16
    BUILDINGS = 8
    POPS = 4
    RESOURCES = 2
    TERRAIN = 1