from __future__ import annotations

from typing import List

from .biome import Biome
from .terrain import Terrain

from obj.worldobj.animal import Animal
from obj.worldobj.worldobjecttype.pop import Pop
from obj.worldobj.worldobjecttype.tree import Tree

from observers import Subject

class Tile(Subject):
    def __init__(self, location, local_coordinates, terrain, biome):
        super().__init__()
        
        self.location = location
        self.chunk_location = local_coordinates
        self.terrain = terrain
        self.biome = biome
        self.pops = []
        self.animals = []
        self.trees = []
        self.colour_override = None
        self.dirty = True
    
    def make_dirty(self):
        self.dirty = True
    
    def mark_rendered(self):
        self.dirty = False
    
    def get_location(self):
        return self.location
    
    def set_location(self, location) -> tuple:
        self.location = location
        self.notify_observers()
    
    def get_pops(self) -> List[Pop]:
        return self.pops
    
    def add_pop(self, pop):
        if len(self.pops) == 0:
            self.notify_observers()
        
        if pop not in self.pops:
            self.pops.append(pop)
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
    
    def get_trees(self) -> List[Tree]:
        return self.trees
    
    def add_tree(self, tree):
        if len(self.tree) == 0:
            self.notify_observers()
        
        self.trees.append(tree)
    
    def remove_tree(self, tree):
        if len(self.tree) > 0:
            self.notify_observers()
        
        self.trees.remove(tree)
    
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