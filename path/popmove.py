from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import obj.worldobj.creatures.pop
    import world.tile

class PopMove:
    def __init__(self, pop: obj.worldobj.creatures.pop.Pop, destination_tile: world.tile.Tile):
        self.pop = pop
        self.destination_tile = destination_tile
        self.progress = 0
        self.invalid = False
    
    def invalidate(self):
        self.invalid = True
    
    def progress_move(self):
        if self.destination_tile.terrain.speed_multiplier == 0:
            self.invalidate()
            return
        
        self.progress += self.pop.speed * self.destination_tile.terrain.speed_multiplier
    
    def is_done(self):
        return self.progress >= 1