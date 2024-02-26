class Temperature:
    COLD = -0.5
    NORMAL = 0
    HOT = 0.5
    
class BiomeType:
    TEMPERATE = 'Temperate'
    ARCTIC = 'Arctic'
    DESERT = 'Desert'
    TROPICAL = 'Tropical'

class Biome():
    def __init__(self, name, colour, fertility=0):
        self.name = name
        self.colour = colour
        self.fertility = fertility
    
    def get_name(self):
        return self.name
    
    def set_name(self, name):
        self.name = name
    
    def get_colour(self):
        return self.colour
    
    def set_colour(self, colour):
        self.colour = colour
    
    def get_tree_spawn_chance(self):
        return self.get_fertility * 50
    
    def get_fertility(self):
        return self.fertility
    
    def set_fertility(self, fertility):
        self.fertility = fertility