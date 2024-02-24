from .biome import Biome
from .terrain import Terrain

class Tile():
    def __init__(self, location, terrain, biome):
        self.location = location
        self.terrain = terrain
        self.biome = biome
        self.pops = []
        self.animals = None
        self.trees = []
    
    def get_location(self):
        return self.location
    
    def set_location(self, location):
        self.location = location
        return self
    
    def get_pops(self):
        return self.pops
    
    def add_pop(self, pop):
        self.pops.append(pop)
        return self
    
    def remove_pop(self, pop):
        self.pops.remove(pop)
        return self
    
    def get_animals(self):
        return self.animal
    
    def add_animal(self, animal):
        self.animals.append(animal)
        return self
    
    def remove_animal(self, animal):
        self.animals.remove(animal)
        return self
    
    def get_terrain(self):
        return self.terrain
    
    def set_terrain(self, terrain):
        self.terrain = terrain
        return self
    
    def get_biome(self) -> Biome:
        return self.biome
    
    def set_biome(self, biome):
        self.biome = biome
        return self
    
    def get_render_info(self):
        """Prepare and return information needed for rendering this tile."""
        # This method can be expanded based on what information the renderer needs
        # Example: Return the most dominant feature of the tile for rendering
        if self.trees:
            # Green colour RGB
            return (0, 255, 0)
        elif self.animals:
            # Brown colour RGB
            return (165, 42, 42)
        elif self.pops:
            # Purple colour RGB
            return (128, 0, 128)
        
        return self.get_terrain_colour()
    
    def get_terrain_colour(self):
        # Combine the terrain and biome colours
        return self.terrain.get_colour()