# TODO: Add difficulty to node, making node take longer to harvest
# TODO: Make node slowly regenerate resources
# TODO: 

from world.worldobject import WorldObject, WORLD_OBJECT_TYPE
from .harvestable import Harvestable, HarvestType
from obj.item import Item, Wood, Stone, Apple

class ResourceNode(WorldObject, Harvestable):
    def __init__(self, name, description, harvestable_resource, resource_amount=1000):
        super().__init__(name=name, description=description, object_type=WORLD_OBJECT_TYPE.RESOURCE_NODE)
        self.resource_amount = resource_amount
        self.harvestable_resource = harvestable_resource
    
    def harvest(self, amount):
        if amount < 0:
            # Negative amount means unlimited resources
            return (self.harvestable_resource, self.resource_amount)
        if amount > self.resource_amount:
            amount = self.resource_amount
            self.resource_amount = 0
        else:
            self.resource_amount -= amount
        
        return (self.harvestable_resource, amount)
    
    def __str__(self):
        return f"ResourceNode: {self.harvestable_resource} {self.resource_amount}"
    
    def get_resource_type(self):
        return self.harvestable_resource
    
    def get_resource_amount(self):
        return self.resource_amount
    
    def is_available(self):
        return self.resource_amount > 0

class NoResource(ResourceNode):
    def __init__(self):
        super().__init__(name='no_resource', description='No resource', harvestable_resource=None, resource_amount=0)
    
    def harvest(self, amount):
        return None
    
    def is_available(self):
        return False

# Enum with different growth speeds for trees
class TreeGrowthSpeed:
    SLOW = 1
    MEDIUM = 2
    FAST = 3
    BOOSTED = 5

class WoodResource(ResourceNode):
    def __init__(self, type, harvest_type: HarvestType=None, harvestable_resource: Item=Wood()):
        super().__init__(name=type, description="Test description tree", harvestable_resource=harvestable_resource)
        self.type = type
        self.harvest_type = harvest_type
        self.harvestable_resource = harvestable_resource
        # TODO: implement resource amount
    
    def __repr__(self):
        return f'{self.type} tree'
    
    def harvest(self, amount):
        return [self.harvestable_resource for i in range(amount)]
    
    # Currently unlimited resources
    # TODO: Add check on resource amount
    def is_harvestable(self):
        return self.harvest_type is not HarvestType.NONE

class Oak(WoodResource):
    def __init__(self):
        super().__init__(type='oak', harvest_type=HarvestType.AXE, harvestable_resource=Wood())

class Cactus(WoodResource):
    def __init__(self):
        super().__init__(type='cactus', harvest_type=HarvestType.SICKLE)

class AppleTree(WoodResource):
    def __init__(self):
        super().__init__(type='apple', harvest_type=HarvestType.BARE_HANDS, harvestable_resource=Apple())

class StoneResource(ResourceNode):
    def __init__(self):
        super().__init__(name='stone', description='A stone resource', harvestable_resource=Stone())