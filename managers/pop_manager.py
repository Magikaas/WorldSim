from __future__ import annotations

from typing import List
from .pop_move_manager import PopMoveManager
from obj.worldobj.pop import Pop

class PopManager():
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PopManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):  # This prevents re-initialization
            self.pops = []
            self.initialized = True
    
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
        self.pops.append(pop)
    
    def remove_pop(self, pop):
        self.pops.remove(pop)
    
    def update_pop(self, pop):
        for i in range(len(self.pops)):
            if self.pops[i].id == pop.id:
                self.pops[i] = pop
                return
    
    def get_pops(self) -> List[Pop]:
        return self.pops
    
    def get_idle_pops(self) -> List[Pop]:
        idle_pops = []
        for pop in self.pops:
            if pop.is_idle():
                idle_pops.append(pop)
        return idle_pops
    
    def move_pop(self, pop, x, y):
        self.pop_move_manager.move_pop(pop, x, y)
    
    def get_pops_within_radius(self, x, y, radius):
        pops = []
        for pop in self.pops:
            if pop.location[0] >= x - radius and pop.location[0] <= x + radius and pop.location[1] >= y - radius and pop.location[1] <= y + radius:
                pops.append(pop)
        return pops
    
    def update(self):
        for pop in self.get_pops():
            pop.update()