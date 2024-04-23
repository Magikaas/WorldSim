from __future__ import annotations
from typing import List, TYPE_CHECKING

from utils.logger import Logger

from .pop_move_manager import PopMoveManager

if TYPE_CHECKING:
    import obj.worldobj.pop

class PopManager():
    _instance = None
    _id_counter = 1
    pops: dict[int, obj.worldobj.pop.Pop] = {}
    
    def __init__(self):
        self.logger = Logger("pop_manager")
    
    def add_pop_move_manager(self, pop_move_manager: PopMoveManager):
        self.pop_move_manager = pop_move_manager
    
    def generate_pop(self, name=None, location=(0, 0), world=None):
        if name is None:
            name = "Pop %s" % len(self.pops)
        
        from obj.worldobj.pop import Pop
        pop = Pop(id=len(self.pops), name=name, location=location, world=world)
        return pop
    
    def add_pop(self, pop: obj.worldobj.pop.Pop):
        if pop.id is None:
            pop.id = self._id_counter
            self._id_counter += 1
        
        self.update_pop(pop)
        self.pops[pop.id].initialise_default_goals()
    
    def remove_pop(self, pop):
        del self.pops[pop.id]
    
    def update_pop(self, pop):
        self.pops[pop.id] = pop
    
    def get_pops(self) -> List[obj.worldobj.pop.Pop]:
        return self.pops.values()
    
    def get_pop(self, id) -> obj.worldobj.pop.Pop:
        return self.pops[id]
    
    def get_idle_pops(self) -> List[obj.worldobj.pop.Pop]:
        idle_pops = []
        for pop in self.pops.values():
            if pop.is_idle():
                idle_pops.append(pop)
        return idle_pops
    
    def get_pops_within_radius(self, x, y, radius):
        pops = []
        for pop in self.pops.values():
            if pop.location[0] >= x - radius and pop.location[0] <= x + radius and pop.location[1] >= y - radius and pop.location[1] <= y + radius:
                pops.append(pop)
        return pops
    
    def give_item_to_pop(self, pop: obj.worldobj.pop.Pop, item):
        self.logger.debug("Giving %sx %s to %s" % (item.amount, item.item.name, pop.name), actor=pop)
        pop.add_item(item)
        self.update_pop(pop)
    
    def kill_pop(self, pop: obj.worldobj.pop.Pop):
        self.logger.debug("Killing pop", actor=pop)
        self.remove_pop(pop)
        self.remove_pop_from_world(pop)
        pop.world.trigger_force_render()
    
    def remove_pop_from_world(self, pop: obj.worldobj.pop.Pop):
        self.logger.debug("Removing pop from world", actor=pop)
        pop.world.get_tile(pop.location).remove_pop(pop)
    
    def update(self):
        dead_pops = []
        for pop in self.get_pops():
            pop.update()
            
            if pop.is_dead():
                dead_pops.append(pop)
        
        for dead_pop in dead_pops:
            self.kill_pop(dead_pop)

pop_manager = PopManager()