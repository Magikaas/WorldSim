from typing import List

from world.worldobject import WorldObject, WORLD_OBJECT_TYPE
from obj.item import ItemStack, Wood, Stone

class Building(WorldObject):
    def __init__(self, name, description, materials:List[ItemStack]):
        self.name = name
        self.description = description
        self.type = WORLD_OBJECT_TYPE.BUILDING
        self.materials = materials
    
    def can_build(self, inventory):
        for material in self.materials:
            if inventory.get_quantity(material.item) < material.amount:
                return False
        return True

class Hut(Building):
    def __init__(self):
        super().__init__(name="Hut", description="A small hut", materials=[ItemStack(Wood(), 10), ItemStack(Stone(), 5)])