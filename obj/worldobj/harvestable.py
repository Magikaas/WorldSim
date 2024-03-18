from typing import Protocol
from enum import Enum

from obj.item import Item

# Enum with types of harvest methods
class HarvestType(Enum):
    NONE = 'none'
    AXE = 'axe'
    BARE_HANDS = 'bare_hands'
    SCYTHE = 'scythe'
    SICKLE = 'sickle'
    PICKAXE = 'pickaxe'
    SHOVEL = 'shovel'

class Harvestable(Protocol):
    harvestable_resource: Item
    
    def harvest(self, amount): ...