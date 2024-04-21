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
    
    
    def get_tile_path_value(self):
        return 1 / self.tile.terrain.speed_multiplier