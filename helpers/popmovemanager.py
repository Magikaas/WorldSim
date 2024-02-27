from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import obj.worldobj.worldobjecttype.pop

class PopMoveManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(PopMoveManager, cls).__new__(cls)
            
            cls._instance.__init__(*args, **kwargs)
        return cls._instance
    
    def __init__(self):
        # Initialize only if not already initialized
        if not hasattr(self, 'initialized'):  # This prevents re-initialization
            self.initialized = True
    
    def set_world(self, world):
        self.world = world
    
    def move_pop(self, pop: obj.worldobj.worldobjecttype.pop.Pop, direction: tuple):
        # print("Moving pop %s to %s" % (pop.location, direction))
        past_chunk = self.world.chunk_manager.get_chunk_at(pop.location)
        past_chunk.make_dirty()
        past_tile = self.world.get_tile(pop.location)
        
        past_tile.remove_pop(pop)
        
        x, y = pop.location[0], pop.location[1]
        
        # X
        x = (x + direction[0]) % self.world.width
        
        if x < 0:
            x = self.world.width + x
        
        # Y
        y = (y + direction[1]) % self.world.height
        
        if y < 0:
            y = self.world.height + y
        
        new_location = (x, y)
        
        pop.set_location(new_location)
        
        tile = self.world.get_tile(new_location)
        
        tile.add_pop(pop)
        
        tile.set_colour_override(pop.colour)