from typing import List

from .biome import Biome
from .terrain import Terrain

from obj.worldobj.animal import Animal
from obj.worldobj.worldobjecttype.pop import Pop
from obj.worldobj.worldobjecttype.tree import Tree

from helpers.popmanager import PopManager

class Tile():
    def __init__(self, location, terrain, biome):
        self.location = location
        self.terrain = terrain
        self.biome = biome
        self.pops = []
        self.animals = []
        self.trees = []
    
    def get_location(self):
        return self.location
    
    def set_location(self, location) -> tuple:
        self.location = location
        return self
    
    def get_pops(self) -> List[Pop]:
        location = self.get_location()
        return PopManager().get_pops_at(location[0], location[1])
    
    def add_pop(self, pop):
        self.pops.append(pop)
        return self
    
    def remove_pop(self, pop):
        self.pops.remove(pop)
        return self
    
    def get_animals(self):
        return self.animals
    
    def add_animal(self, animal):
        self.animals.append(animal)
        return self
    
    def remove_animal(self, animal):
        self.animals.remove(animal)
        return self
    
    def get_trees(self) -> List[Tree]:
        return self.trees
    
    def add_tree(self, tree):
        self.trees.append(tree)
        return self
    
    def remove_tree(self, tree):
        self.trees.remove(tree)
        return self
    
    def get_terrain(self) -> Terrain:
        return self.terrain
    
    def set_terrain(self, terrain):
        self.terrain = terrain
        return self
    
    def get_biome(self) -> Biome:
        return self.biome
    
    def set_biome(self, biome):
        self.biome = biome
        return self