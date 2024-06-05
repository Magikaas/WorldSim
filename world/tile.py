from __future__ import annotations
from typing import TYPE_CHECKING

import obj.worldobj.animal
from obj.worldobj.building import Building
from obj.worldobj.resourcenode import NoResource

from .biome import Biome
from .terrain import Terrain

from observer import Subject

from utils.logger import Logger

from managers.logger_manager import logger_manager

from object_types import Location

if TYPE_CHECKING:
    import obj.worldobj.resourcenode
    import obj.worldobj.pop
    import obj.worldobj
    import obj.worldobj.building

class Tile(Subject):
    pops: dict[str, obj.worldobj.pop.Pop]
    animals: list[obj.worldobj.animal.Animal] = {}
    resourcenode: obj.worldobj.resourcenode.ResourceNode = NoResource()
    terrain: Terrain
    biome: Biome
    building: Building
    location: Location
    
    def __init__(self, location: Location, local_coordinates: Location, terrain: Terrain, biome: Biome):
        super().__init__()
        
        self.logger = Logger("Tile", logger_manager)
        
        self.location = location
        self.local_coordinates = local_coordinates # Coordinates within its chunk
        
        self.terrain = terrain
        self.biome = biome
        
        self.pops = {}
        
        self.colour_override = None
        self.dirty = True
    
    def add_pop(self, pop):
        if len(self.pops) == 0:
            self.notify_observers()
        
        if pop not in self.pops:
            self.pops[pop.id] = pop
            self.colour_override = pop.colour
        else:
            print("Pop %s already exists in tile %s" % (pop, self))
    
    def remove_pop(self, pop):
        if len(self.pops) > 0:
            self.notify_observers()
        
        del self.pops[pop.id]
    
    def add_animal(self, animal):
        if len(self.animals) == 0:
            self.notify_observers()
        
        self.animals.append(animal)
    
    def remove_animal(self, animal):
        if len(self.animals) > 0:
            self.notify_observers()
        
        self.animals.remove(animal)
    
    def add_resourcenode(self, node):
        if self.resourcenode is not None:
            # print("Attempting to add resourcenode to tile with existing node")
            return False
        else:
            self.notify_observers()
            self.resourcenode = node
            return True
    
    def remove_resourcenode(self):
        if self.resourcenode is not None:
            self.notify_observers()
            del self.resourcenode
    
    def has_building(self):
        return hasattr(self, "building") and self.building is not None
    
    def build(self, building: obj.worldobj.building.Building, pop: obj.worldobj.pop.Pop):
        inventory = pop.inventory
        
        if self.has_building():
            self.logger.error("Tile already has a building.")
            return False
        
        if building.can_build(inventory):
            # Expend resources from inventory and build building
            for material in building.materials:
                pop.inventory.remove_item(material)
            
            self.building = building
            self.notify_observers()
            return True
        else:
            return False
    
    def remove_building(self):
        del self.building
    
    def has_colour_override(self):
        return self.colour_override is not None
    
    def get_pathing_cost(self):
        return self.terrain.get_pathing_cost()