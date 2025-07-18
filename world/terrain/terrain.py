from dataclasses import field, dataclass
from typing import Type
from object_types import Colour
from obj.item.item import Item

class TerrainHeight:
    OCEAN = -1
    SHALLOW_COASTAL_WATER = -0.3
    RIVER = -0.1
    LAND = 0.1
    HILLS = 0.6
    MOUNTAIN = 0.8
    MOUNTAIN_PEAK = 1

@dataclass
class Terrain():
    name: str
    colour: Colour
    speed_multiplier: float = 1.0   
    fertility: int = 1
    can_spawn_resource: bool = False
    possible_resources: dict[int, Type] = field(default_factory=dict)
    
    def get_pathing_cost(self):
        return 1 / self.speed_multiplier