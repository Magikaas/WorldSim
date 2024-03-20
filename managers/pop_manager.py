from __future__ import annotations
from typing import List

from obj.worldobj.pop import Pop

from utils.logger import Logger

from .pop_move_manager import PopMoveManager

class PopManager():
    _instance = None
    
    _id_counter = 1

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PopManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):  # This prevents re-initialization
            self.pops = {}
            self.initialized = True
            self.logger = Logger("pop_manager")
    
    def get_pops(self) -> List[Pop]:
        return self.pops
    
    def add_pop_move_manager(self, pop_move_manager: PopMoveManager):
        self.pop_move_manager = pop_move_manager
    
    def generate_pop(self, name=None, location=(0, 0), world=None):
        if name is None:
            name = "Pop %s" % len(self.pops)
        
        pop = Pop(id=len(self.pops), name=name, location=location, world=world)
        return pop
    
    def add_pop(self, pop: Pop):
        if pop.id is None:
            pop.id = self._id_counter
            self._id_counter += 1
        
        self.update_pop(pop)
        self.pops[pop.id].initialise_default_goals()
    
    def remove_pop(self, pop):
        del self.pops[pop.id]
    
    def update_pop(self, pop):
        self.pops[pop.id] = pop
    
    def get_pops(self) -> List[Pop]:
        return self.pops.values()
    
    def get_pop(self, id) -> Pop:
        return self.pops[id]
    
    def get_idle_pops(self) -> List[Pop]:
        idle_pops = []
        for pop in self.pops.values():
            if pop.is_idle():
                idle_pops.append(pop)
        return idle_pops
    
    def move_pop(self, pop, x, y):
        self.pop_move_manager.move_pop(pop, x, y)
    
    def get_pops_within_radius(self, x, y, radius):
        pops = []
        for pop in self.pops.values():
            if pop.location[0] >= x - radius and pop.location[0] <= x + radius and pop.location[1] >= y - radius and pop.location[1] <= y + radius:
                pops.append(pop)
        return pops
    
    def give_item_to_pop(self, pop: Pop, item):
        self.logger.debug("Giving %sx %s to pop %s" % (item.amount, item.item.name, pop.name))
        pop.add_item(item)
        self.update_pop(pop)
    
    def update(self):
        for pop in self.get_pops():
            pop.update()
        
        self.pop_move_manager.handle_moves()