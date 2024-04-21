from __future__ import annotations

from world.tile import Tile

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    import world

class TileManager:
    tiles: list[list[Tile]]
    dirty: bool = True
    
    def __init__(self, chunk: world.Chunk):
        self.chunk = chunk
        tiles: list[list[Tile]] = []
        for i in range(chunk.size):
            tiles_row = []
            for j in range(chunk.size):
                tiles_row.append(0)
            tiles.append(tiles_row)
        self.tiles = tiles
    
    def add_tile(self, tile: Tile):
        if len(self.tiles) < tile.local_coordinates[0] or len(self.tiles[0]) < tile.local_coordinates[1]:
            print("Tile	location out of bounds:", tile.get_local_coordinates()[0], tile.get_local_coordinates()[1])
            return
        self.tiles[tile.local_coordinates[0]][tile.local_coordinates[1]] = tile
    
    def remove_tile(self, tile: Tile):
        self.tiles.remove(tile)
    
    def get_dirty_tiles(self) -> List[List[Tile]]:
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
        x, y = location
        
        for tile_row in self.tiles:
            for tile in tile_row:
                tx, ty = tile.location
                if tx >= x - radius and tx <= x + radius and ty >= y - radius and ty <= y + radius:
                    tiles.append(tile)
        return tiles