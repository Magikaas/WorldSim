from helpers.tilemanager import TileManager
from observers import Subject, RenderableObserver

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
        return self.tiles
    
    def is_dirty(self):
        return self.dirty
    
    def mark_rendered(self):
        self.dirty = False
    
    def make_dirty(self):
        self.dirty = True
    
    def notify(self, subject):
        self.notify_observers()
        subject.make_dirty()