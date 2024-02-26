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
        self.colour_override = None
        self.render_me = True
    
    def mark_for_render(self):
        self.render_me = True
        return self
    
    def mark_rendered(self):
        self.render_me = False
        return self
    
    def get_location(self):
        return self.location
    
    def set_location(self, location) -> tuple:
        self.location = location
        return self
    
    def get_pops(self) -> List[Pop]:
        return self.pops
    
    def add_pop(self, pop):
        if len(self.pops) == 0:
            self.mark_for_render()
        
        if pop not in self.pops:
            self.pops.append(pop)
            return self
        else:
            print("Pop %s already exists in tile %s" % (pop, self))
            return self
    
    def remove_pop(self, pop):
        self.pops.remove(pop)
        
        if len(self.pops) == 0:
            self.mark_for_render()
        
        return self
    
    def get_animals(self):
        return self.animals
    
    def add_animal(self, animal):
        if len(self.animals) == 0:
            self.mark_for_render()
            
        self.animals.append(animal)
        return self
    
    def remove_animal(self, animal):
        self.animals.remove(animal)
        
        if len(self.animals) == 0:
            self.mark_for_render()
        
        return self
    
    def get_trees(self) -> List[Tree]:
        return self.trees
    
    def add_tree(self, tree):
        if len(self.tree) == 0:
            self.mark_for_render()
        
        self.trees.append(tree)
        return self
    
    def remove_tree(self, tree):
        self.trees.remove(tree)
        
        if len(self.tree) == 0:
            self.mark_for_render()
        
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
    
    def has_colour_override(self):
        return self.colour_override is not None
    
    def get_colour_override(self):
        return self.colour_override
    
    def set_colour_override(self, colour):
        self.colour_override = colour
        return self