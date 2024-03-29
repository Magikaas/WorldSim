from world.tilemanager import TileManager
from observer import Subject, RenderableObserver

class Chunk(Subject, RenderableObserver):
    def __init__(self, location, size=16):
        super().__init__()
        
        self.location = location
        self.dirty = True # True if the chunk has been modified since the last time it was rendered
        self.size = size
        self.tile_manager = TileManager(chunk=self)
        self.dirty = True
    
    def get_tile_manager(self) -> TileManager:
        return self.tile_manager
    
    def get_location(self):
        return self.location
    
    def get_tiles(self):
        return self.tile_manager.get_tiles()
    
    def is_dirty(self):
        return self.dirty
    
    def mark_rendered(self):
        self.dirty = False
    
    def make_dirty(self):
        self.dirty = True
    
    def notify(self, subject):
        self.notify_observers()
        subject.make_dirty()
    
    def get_terrains(self):
        tiles = self.get_tiles()
        
        terrains = []
        
        for tile in tiles:
            if terrains.count(tile.get_terrain()) == 0:
                terrains.append(tile.get_terrain())
        
        return terrains