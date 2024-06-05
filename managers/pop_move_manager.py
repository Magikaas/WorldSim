from __future__ import annotations

from path.popmove import PopMove
from utils.logger import Logger

from managers.logger_manager import logger_manager

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    import obj.worldobj.pop
    import world
    import path

class PopMoveManager:
    _instance = None
    popmoves: dict[int, List[PopMove]] = {}
    world: world.World

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(PopMoveManager, cls).__new__(cls)
            
        return cls._instance
    
    def __init__(self):
        self.logger = Logger("pop_move_manager", logger_manager)
    
    def handle_moves(self):
        # Move pops along their paths
        for popid in self.popmoves:
            if len(self.popmoves[popid]) == 0:
                continue
            
            move = self.popmoves[popid][0]
            
            if move.pop.location == move.destination_tile.location:
                # Pop is already at the destination
                self.popmoves[popid] = self.popmoves[popid][1:]
                continue
            
            move.progress_move()
            
            if move.is_done():
                # self.logger.debug("Pop %s has arrived at %s" % (move.pop.name, move.destination_tile.location))
                self.move_pop_to_tile(pop=move.pop, destination=move.destination_tile)
                self.popmoves[popid] = self.popmoves[popid][1:]
    
    def empty_moves(self, pop):
        self.popmoves[pop.id] = []
    
    def get_move_for_pop(self, pop: obj.worldobj.pop.Pop):
        if pop.id not in self.popmoves or len(self.popmoves[pop.id]) == 0:
            return None
        else:
            return self.popmoves[pop.id][0]
    
    def move_pop(self, popmove: path.PopMove):
        # print("Moving pop %s to %s" % (popmove.pop.name, popmove.destination_tile.location))
        if popmove.pop.id not in self.popmoves:
            self.popmoves[popmove.pop.id] = []
        
        self.popmoves[popmove.pop.id].append(popmove)
    
    def move_pop_to_tile(self, pop: obj.worldobj.pop.Pop, destination: world.tile.Tile):
        # print("Moving pop %s to %s" % (pop.location, direction))
        total_distance = abs(pop.location[0] - destination.location[0]) + abs(pop.location[1] - destination.location[1])
        
        if (total_distance > 2 and total_distance < 250) or total_distance == 0:
            self.logger.error("Pop %s is moving more than 1 tile at a time. This is not allowed" % pop.name)
            return
        
        past_chunk = self.world.chunk_manager.get_chunk_at(pop.location)
        past_chunk.dirty = True
        past_tile = self.world.get_tile(pop.location)
        
        past_tile.remove_pop(pop)
        
        target_x, target_y = destination.location[0], destination.location[1]
        
        new_location = (target_x, target_y)
        
        pop.location = new_location
        
        tile = self.world.get_tile(new_location)
        
        tile.add_pop(pop)

pop_move_manager = PopMoveManager()