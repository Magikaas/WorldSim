from __future__ import annotations
from typing import List, TYPE_CHECKING
from pathfinding.core.node import Node


from .biome import Biome
from .terrain import Terrain

from observer import Subject

if TYPE_CHECKING:
    import obj.worldobj.resourcenode
    import obj.worldobj.pop
    import obj.worldobj

class Tile(Subject):
    def __init__(self, location: tuple, local_coordinates: tuple, terrain: Terrain, biome: Biome):
        super().__init__()
        
        self.location = location
        self.local_coordinates = local_coordinates # Coordinates within its chunk
        
        self.terrain = terrain
        self.biome = biome
        
        self.pops = []
        self.animals = []
        self.resourcenode = None
        self.building = None
        
        self.colour_override = None
        self.dirty = True
    
    def make_dirty(self):
        self.dirty = True
    
    def mark_rendered(self):
        self.dirty = False
    
    def get_local_coordinates(self):
        return self.local_coordinates
    
    def set_local_coordinates(self, local_coordinates) -> tuple:
        self.local_coordinates = local_coordinates
        self.notify_observers()
    
    def get_pops(self) -> List[obj.worldobj.pop.Pop]:
        return self.pops
    
    def add_pop(self, pop):
        if len(self.pops) == 0:
            self.notify_observers()
        
        if pop not in self.pops:
            self.pops.append(pop)
            self.set_colour_override(pop.colour)
        else:
            print("Pop %s already exists in tile %s" % (pop, self))
    
    def remove_pop(self, pop):
        if len(self.pops) > 0:
            self.notify_observers()
        
        self.pops.remove(pop)
    
    def get_animals(self):
        return self.animals
    
    def add_animal(self, animal):
        if len(self.animals) == 0:
            self.notify_observers()
        
        self.animals.append(animal)
    
    def remove_animal(self, animal):
        if len(self.animals) > 0:
            self.notify_observers()
        
        self.animals.remove(animal)
    
    def get_resourcenode(self) -> obj.worldobj.resourcenode.ResourceNode:
        return self.resourcenode
    
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
            self.resourcenode = None
    
    def build(self, building: obj.worldobj.Building, pop: obj.worldobj.pop.Pop):
        inventory = pop.get_inventory()
        
        if building.can_build(inventory):
            # Expend resources from inventory and build building
            for material in building.get_required_items():
                pop.inventory.remove_item(material)
            
            self.building = building
            self.notify_observers()
            return True
        else:
            return False
    
    def get_building(self) -> obj.worldobj.Building:
        return self.building
    
    def remove_building(self):
        self.building = None
    
    def get_terrain(self) -> Terrain:
        return self.terrain
    
    def set_terrain(self, terrain):
        self.terrain = terrain
        self.notify_observers()
    
    def get_biome(self) -> Biome:
        return self.biome
    
    def set_biome(self, biome):
        self.biome = biome
        self.notify_observers()
    
    def has_colour_override(self):
        return self.colour_override is not None
    
    def get_colour_override(self):
        return self.colour_override
    
    def set_colour_override(self, colour):
        self.colour_override = colour
        self.notify_observers()
    
    def get_path_node(self) -> Node:
        return Node(self.location[0], self.location[1])