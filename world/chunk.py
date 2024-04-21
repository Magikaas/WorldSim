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
    
    def get_average_pathing_cost(self):
        tiles = self.get_tiles()
        
        counter = 0
        
        total_cost = 0
        for tile_row in tiles:
            for tile in tile_row:
                total_cost += tile.get_pathing_cost()
                counter += 1
        
        return total_cost / counter