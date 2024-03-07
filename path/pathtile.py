from __future__ import annotations

from world.terrain import *

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import world
    import world.tile

class PathTile:
    def __init__(self, tile: world.tile.Tile):
        self.tile = tile
        self.total_path_length = 0
    
    def get_tile(self):
        return self.tile
    
    def set_tile(self, tile):
        self.tile = tile
    
    def get_tile_path_value(self):
        return 1 / self.tile.terrain.speed_multiplier
        # if self.tile.get_terrain() == Ocean:
        #     return 10
        # elif self.tile.get_terrain() == ShallowCoastalWater:
        #     return 5
        # elif self.tile.get_terrain() == River:
        #     return 5
        # elif self.tile.get_terrain() == Land:
        #     return 1
        # elif self.tile.get_terrain() == Hills:
        #     return 3
        # elif self.tile.get_terrain() == Mountain:
        #     return 6
        # elif self.tile.get_terrain() == MountainPeak:
        #     return 35
        # else:
        #     return 1000