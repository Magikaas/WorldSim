import numpy as np

from world.tile import Tile

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    import world

class TileManager:
    def __init__(self, world: 'world.World'):
        self.world = world
        self.tiles = []
    
    def initialize_tiles(self):
        self.tiles = np.zeros(self.world.get_size(), dtype=Tile)
    
    def add_tile(self, tile: Tile):
        if len(self.tiles) < tile.get_location()[0] or len(self.tiles[0]) < tile.get_location()[1]:
            print("Tile	location out of bounds: %s" % tile.get_location())
            return
        self.tiles[tile.get_location()[0]][tile.get_location()[1]] = tile
        return self
    
    def remove_tile(self, tile: Tile):
        self.tiles.remove(tile)
        return self
    
    def get_tiles(self) -> List[Tile]:
        return self.tiles
    
    def get_tile(self, location) -> Tile:
        if len(self.tiles) < location[0] or len(self.tiles[0]) < location[1]:
            print("Fetching tile from out of bounds: %s" % location)
            return
        else:
            return self.tiles[location[0]][location[1]]
    
    def get_tiles_within_radius(self, location, radius) -> List[Tile]:
        tiles = []
        for tile in self.tiles:
            if tile.get_location()[0] >= location[0] - radius and tile.get_location()[0] <= location[0] + radius and tile.get_location()[1] >= location[1] - radius and tile.get_location()[1] <= location[1] + radius:
                tiles.append(tile)
        return tiles