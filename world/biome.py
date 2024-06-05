from enum import Enum
from dataclasses import dataclass

from object_types import Location

class Temperature:
    COLD = -0.5
    NORMAL = 0
    HOT = 0.5
    
class BiomeType(Enum):
    TEMPERATE = 'Temperate'
    ARCTIC = 'Arctic'
    DESERT = 'Desert'
    TROPICAL = 'Tropical'

@dataclass
class Biome():
    name: str
    colour: Location
    fertility: int = 0
    
    def get_tree_spawn_chance(self):
        return self.fertility * 50