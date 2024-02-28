# TODO: Add difficulty to node, making node take longer to harvest
# TODO: Make node slowly regenerate resources
# TODO: 

from obj.worldobject import WorldObject, WORLD_OBJECT_TYPE
from .harvestable import Harvestable

class ResourceNode(WorldObject, Harvestable):
    def __init__(self, name, description, harvestable_resource, resource_amount=1000):
        super().__init__(name=name, description=description, object_type=WORLD_OBJECT_TYPE.RESOURCE_NODE)
        self.resource_amount = resource_amount
    
    def harvest(self, amount):
        if amount > self.resource_amount:
            amount = self.resource_amount
            self.resource_amount = 0
        else:
            self.resource_amount -= amount
    
    def __str__(self):
        return f"ResourceNode: {self.harvestable_resource} {self.resource_amount}"
    
    def get_resource_type(self):
        return self.harvestable_resource
    
    def get_resource_amount(self):
        return self.resource_amount
    
    def is_available(self):
        return self.resource_amount > 0