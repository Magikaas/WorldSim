from .biome import Biome
from .terrain import Terrain

class Tile():
    def __init__(self, location, terrain, biome):
        self.location = location
        self.terrain = terrain
        self.biome = biome
        self.world_obj = None
        self.pops = []
        self.animal = None
    
    def get_pops(self):
        return self.pops
    
    def add_pops(self, pop):
        self.pops.append(pop)
        return self
    
    def remove_pops(self, pop):
        self.pops.remove(pop)
        return self
    
    def get_animal(self):
        return self.animal
    
    def set_animal(self, animal):
        self.animal = animal
        return self
    
    def get_location(self):
        return self.location
    
    def set_location(self, location):
        self.location = location
        return self
    
    def get_terrain(self):
        return self.terrain
    
    def set_terrain(self, terrain):
        self.terrain = terrain
        return self
    
    def get_biome(self):
        return self.biome
    
    def set_biome(self, biome):
        self.biome = biome
        return self
    
    def get_world_obj(self):
        return self.world_obj
    
    def set_world_obj(self, world_obj):
        self.world_obj = world_obj
        return self
    
    def get_combined_terrain_colour(self):
        # Combine the terrain and biome colours
        return self.terrain.get_colour() + self.biome.get_colour()