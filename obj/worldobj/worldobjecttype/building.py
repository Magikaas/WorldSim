from typing import List

from world.worldobject import WorldObject, WORLD_OBJECT_TYPE
from obj.item import ItemStack

class Building(WorldObject):
    def __init__(self, name, description, materials=List[ItemStack]):
        self.name = name
        self.description = description
        self.type = WORLD_OBJECT_TYPE.BUILDING
        self.materials = materials
    
    def get_type(self):
        return self.type
    
    def get_required_items(self):
        return self.materials

class Hut(Building):
    def __init__(self):
        super().__init__(name="Hut", description="A small hut", materials=[ItemStack("Wood", 10), ItemStack("Stone", 5)])