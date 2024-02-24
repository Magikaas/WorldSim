class TerrainHeight:
    OCEAN = -1
    SHALLOW_COASTAL_WATER = -0.5
    RIVER = -0.1
    LAND = 0.1
    HILLS = 0.6
    MOUNTAIN = 0.8
    MOUNTAIN_PEAK = 1

class Terrain():
    def __init__(self, name, colour):
        self.name = name
        self.colour = colour
    
    def get_name(self):
        return self.name
    
    def set_name(self, name):
        self.name = name
        return self
    
    def get_colour(self) -> tuple:
        return self.colour
    
    def set_colour(self, colour):
        self.colour = colour
        return self