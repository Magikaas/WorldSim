# TODO: Add difficulty to node, making node take longer to harvest
# TODO: Make node slowly regenerate resources
# TODO: 

from dataclasses import dataclass, field
from obj.item.item import Axe, BareHands, ItemStack, Pickaxe, Tool
from world.worldobject import WorldObject, WORLD_OBJECT_TYPE
from .harvestable import Harvestable, HarvestType
from obj.item import Item, Wood, Stone, Apple

@dataclass
class ResourceNode(WorldObject, Harvestable):
    name: str = 'resource_node'
    description: str = 'A resource node'
    harvest_tool: Tool|None = None
    harvestable_resource: Item = None
    resource_amount: int = 1000
    
    def harvest(self, amount):
        if amount < 0:
            # Negative amount means unlimited resources
            return (self.harvestable_resource, self.resource_amount)
        if amount > self.resource_amount:
            amount = self.resource_amount
            self.resource_amount = 0
        else:
            self.resource_amount -= amount
        
        harvested_items = ItemStack(self.harvestable_resource, amount)
        return harvested_items
    
    def __str__(self):
        return f"ResourceNode: {self.harvestable_resource} {self.resource_amount}"
    
    def is_available(self):
        return self.resource_amount > 0

@dataclass
class NoResource(ResourceNode):
    name: str = 'no_resource'
    description: str = 'No resource'
    harvestable_resource: Item = None
    resource_amount: int = 0

# Enum with different growth speeds for trees
class TreeGrowthSpeed:
    SLOW = 1
    MEDIUM = 2
    FAST = 3
    BOOSTED = 5

@dataclass
class WoodResource(ResourceNode):
    name: str = 'wood_resource'
    description: str = 'A tree resource'
    harvest_tool: Tool|None = field(default_factory=Axe)
    harvestable_resource: Item = field(default_factory=Wood)
    
    def __repr__(self):
        return f'{self.type} tree'
    
    def harvest(self, amount):
        return [self.harvestable_resource for i in range(amount)]
    
    # Currently unlimited resources
    # TODO: Add check on resource amount
    def is_harvestable(self):
        return self.harvest_tool is not HarvestType.NONE

@dataclass
class Oak(WoodResource):
    name: str = 'oak'
    harvest_tool: Tool = field(default_factory=Axe)
    harvestable_resource: Item = field(default_factory=Wood)

@dataclass
class Cactus(WoodResource):
    name: str = 'cactus'
    harvest_tool: Tool = field(default_factory=Axe)
    harvestable_resource: Item = field(default_factory=Wood)

@dataclass
class AppleTree(WoodResource):
    name: str = 'apple_tree'
    harvest_tool: Tool = field(default_factory=BareHands)
    harvestable_resource: Item = field(default_factory=Apple)

@dataclass
class StoneResource(ResourceNode):
    name: str
    description: str = 'A stone resource'
    harvest_tool: Tool|None = field(default_factory=Pickaxe)
    harvestable_resource: Item = field(default_factory=Stone)