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
            self.popmoves = []
            self.initialized = True
    
    def set_world(self, world: world.World):
        self.world = world
    
    def handle_moves(self):
        for move in self.popmoves:
            move.progress_move()
            
            if move.is_done():
                self.move_pop_to_tile(pop=move.pop, destination=move.destination_tile)
                self.popmoves.remove(move)
    
    def get_move_for_pop(self, pop: obj.worldobj.pop.Pop):
        for move in self.popmoves:
            if move.pop.id == pop.id and move.invalid == False and move.is_done() == False:
                return move
        return None
    
    def move_pop(self, popmove: path.PopMove):
        for move in self.popmoves:
            if move.pop.id == popmove.pop.id:
                # Do not add another move for a pop that is already moving, this is an error
                print("Pop %s is already moving" % popmove.pop.name)
                return
        
        self.popmoves.append(popmove)
    
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