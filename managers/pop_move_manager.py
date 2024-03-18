from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import obj.worldobj.pop
    import world
    import path

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
            self.popmoves = {}
            self.initialized = True
    
    def set_world(self, world: world.World):
        self.world = world
    
    def handle_moves(self):
        # Move pops along their paths
        for popid in self.popmoves:
            if len(self.popmoves[popid]) == 0:
                continue
            move = self.popmoves[popid][0]
            
            move.progress_move()
            
            if move.is_done():
                # print("Pop %s has arrived at %s" % (move.pop.name, move.destination_tile.location))
                self.move_pop_to_tile(pop=move.pop, destination=move.destination_tile)
                self.popmoves[popid] = self.popmoves[popid][1:]
            
    
    def get_move_for_pop(self, pop: obj.worldobj.pop.Pop):
        if pop not in self.popmoves or len(self.popmoves[pop.id]) == 0:
            return None
        else:
            return self.popmoves[pop][0]
    
    def move_pop(self, popmove: path.PopMove):
        # print("Moving pop %s to %s" % (popmove.pop.name, popmove.destination_tile.location))
        if popmove.pop.id not in self.popmoves:
            self.popmoves[popmove.pop.id] = []
        
        self.popmoves[popmove.pop.id].append(popmove)
    
    def move_pop_to_tile(self, pop: obj.worldobj.pop.Pop, destination: world.tile.Tile):
        # print("Moving pop %s to %s" % (pop.location, direction))
        past_chunk = self.world.chunk_manager.get_chunk_at(pop.location)
        past_chunk.make_dirty()
        past_tile = self.world.get_tile(pop.location)
        
        past_tile.remove_pop(pop)
        
        target_x, target_y = destination.location[0], destination.location[1]
        
        new_location = (target_x, target_y)
        
        pop.set_location(new_location)
        
        tile = self.world.get_tile(new_location)
        
        tile.add_pop(pop)