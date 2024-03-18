from __future__ import annotations

from world.tile import Tile

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    import world

class TileManager:
    def __init__(self, chunk: world.Chunk):
        self.chunk = chunk
        tiles = []
        for i in range(chunk.size):
            tiles_row = []
            for j in range(chunk.size):
                tiles_row.append(0)
            tiles.append(tiles_row)
        self.tiles = tiles
    
    def initialize_tiles(self):
        for x in range(self.chunk.get_size()):
            for y in range(self.chunk.get_size()):
                chunk_x = self.chunk.location[0] * self.chunk.size + x
                chunk_y = self.chunk.location[1] * self.chunk.size + y
                self.tiles.append(Tile(location=(chunk_x, chunk_y), local_coordinates=(x, y), terrain=None, biome=None))
    
    def add_tile(self, tile: Tile):
        if len(self.tiles) < tile.local_coordinates[0] or len(self.tiles[0]) < tile.local_coordinates[1]:
            print("Tile	location out of bounds:", tile.get_local_coordinates()[0], tile.get_local_coordinates()[1])
            return
        self.tiles[tile.local_coordinates[0]][tile.local_coordinates[1]] = tile
    
    def remove_tile(self, tile: Tile):
        self.tiles.remove(tile)
    
    def get_tiles(self) -> List[Tile]:
        return self.tiles
    
    def get_dirty_tiles(self) -> List[Tile]:
        dirty_tiles = []
        for tile_row in self.tiles:
            dirty_row = []
            for tile in tile_row:
                if tile.dirty:
                    dirty_row.append(tile)
            dirty_tiles.append(dirty_row)
        return dirty_tiles
    
    def get_tile(self, location) -> Tile:
        return self.tiles[location[0]][location[1]]
    
    def get_tiles_within_radius(self, location, radius) -> List[Tile]:
        tiles = []
        for tile in self.tiles:
            if tile.get_location()[0] >= location[0] - radius and tile.get_location()[0] <= location[0] + radius and tile.get_location()[1] >= location[1] - radius and tile.get_location()[1] <= location[1] + radius:
                tiles.append(tile)
        return tiles