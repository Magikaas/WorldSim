from .worldobjecttype.resourcenode import ResourceNode
from .worldobjecttype.harvestable import HarvestType

from obj.item import Item, Wood

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