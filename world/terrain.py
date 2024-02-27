class TerrainHeight:
    OCEAN = -1
    SHALLOW_COASTAL_WATER = -0.5
    RIVER = -0.1
    LAND = 0.1
    HILLS = 0.6
    MOUNTAIN = 0.8
    MOUNTAIN_PEAK = 1

class Terrain():
    def __init__(self, name, colour, speed_multiplier=1.0):
        self.name = name
        self.colour = colour
        self.speed_multiplier = speed_multiplier
    
    def get_name(self):
        return self.name
    
    def set_name(self, name):
        self.name = name
    
    def get_colour(self) -> tuple:
        return self.colour
    
    def set_colour(self, colour):
        self.colour = colour
    
    def get_speed_multiplier(self):
        return self.speed_multiplier
    
    def set_speed_multiplier(self, speed_multiplier):
        self.speed_multiplier = speed_multiplier