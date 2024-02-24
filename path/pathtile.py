from worldgen.tile import Tile
from worldgen.biome import Biome, BiomeType
from worldgen.terraintype import *

class PathTile:
    def __init__(self, tile: Tile):
        self.tile = tile
        self.total_path_length = 0
    
    def get_tile(self):
        return self.tile
    
    def set_tile(self, tile):
        self.tile = tile
        return self
    
    def get_total_path_length(self):
        return self.total_path_length
    
    def set_total_path_length(self, total_path_length):
        self.total_path_length = total_path_length
        return self
    
    def get_tile_path_value(self):
        if self.tile.get_terrain() == Ocean:
            return 10
        elif self.tile.get_terrain() == ShallowCoastalWater:
            return 5
        elif self.tile.get_terrain() == River:
            return 5
        elif self.tile.get_terrain() == Land:
            return 1
        elif self.tile.get_terrain() == Hills:
            return 3
        elif self.tile.get_terrain() == Mountain:
            return 6
        elif self.tile.get_terrain() == MountainPeak:
            return 35
        else:
            return 1000