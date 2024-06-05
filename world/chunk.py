from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder, DiagonalMovement

from world.tilemanager import TileManager
from observer import Subject, RenderableObserver

class Chunk(Subject, RenderableObserver):
    tile_manager: TileManager
    def __init__(self, location, size=16):
        super().__init__()
        
        self.initialised = False
        self.location = location
        self.dirty = True # True if the chunk has been modified since the last time it was rendered
        self.size = size
        self.tile_manager = TileManager(chunk=self)
        self.dirty = True
        
        self.best_pathing_tile = None
    
    def initialise(self):
        self.initialised = True
        return self
    
    def get_tiles(self):
        return self.tile_manager.tiles
    
    def is_dirty(self):
        return self.dirty
    
    def notify(self, subject):
        self.notify_observers()
        subject.dirty = True
    
    def get_terrains(self):
        tiles = self.get_tiles()
        
        terrains = []
        
        for tile_row in tiles:
            for tile in tile_row:
                if terrains.count(tile.terrain) == 0:
                    terrains.append(tile.terrain)
        
        return terrains
    
    # Get tile with best paths to all borders of the chunk
    def get_best_pathing_tile(self):
        if self.best_pathing_tile is not None:
            return self.best_pathing_tile
        
        best_pathing_cost = 0
        nodepath = None
        
        pathfinder = AStarFinder(diagonal_movement=DiagonalMovement.always)
        
        # Only calculate from the middle 16 (4x4) tiles
        for x in range(4):
            for y in range(4):
                tile = self.get_tiles()[x + 4][y + 4]
                
                gridnodes = [[0 for i in range(self.size)] for j in range(self.size)]
                
                border_tile_coordinates = [(self.size // 2, y), (self.size - 1, y), (x, 0), (x, self.size - 1)]
                
                # Calculate pathing cost to all borders
                pathing_cost = 0
                
                tiles = self.get_tiles()
                
                for tile_row in tiles:
                    for tile in tile_row:
                        gridnodes[tile.local_coordinates[0]][tile.local_coordinates[1]] = (1 / tile.terrain.speed_multiplier if tile.terrain.speed_multiplier > 0 else 0)
                
                grid = Grid(width=self.size, height=self.size, matrix=gridnodes, grid_id="chunk_%sx%s" % (self.location[0], self.location[1]))
                
                for border_tile_coordinate in border_tile_coordinates:
                    target_x, target_y = border_tile_coordinate
                    
                    while nodepath is None:
                        try:
                            nodepath, runs = pathfinder.find_path(start=grid.node(x, y), end=grid.node(target_x, target_y), graph=grid)
                        except Exception as e:
                            print("Error finding path:", e)
                    
                    # Calculate pathing cost based on cost of nodes in nodepath
                    for node in nodepath:
                        pathing_cost += 1 / node.weight
                
                if pathing_cost > best_pathing_cost or self.best_pathing_tile is None:
                    tile = self.get_tiles()[x][y]
                    best_pathing_cost = pathing_cost
                    self.best_pathing_tile = tile
            
        return self.best_pathing_tile
    
    def get_average_pathing_cost(self):
        tiles = self.get_tiles()
        
        counter = 0
        
        total_cost = 0
        for tile_row in tiles:
            for tile in tile_row:
                total_cost += tile.get_pathing_cost()
                counter += 1
        
        return total_cost / counter