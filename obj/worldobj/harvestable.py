from typing import Protocol
from enum import Enum

from obj.item import Item, Axe, Pickaxe

# Enum with types of harvest methods
class HarvestType(Enum):
    NONE = 'none'
    AXE = Axe
    BARE_HANDS = 'bare_hands'
    SCYTHE = 'scythe'
    SICKLE = 'sickle'
    PICKAXE = Pickaxe
    SHOVEL = 'shovel'

class Harvestable(Protocol):
    harvestable_resource: Item
    
    def harvest(self, amount): ...