from typing import List
from obj.worldobj.worldobjecttype.pop import Pop
from .popmovemanager import PopMoveManager

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
    
    def add_pop_move_manager(self, pop_move_manager: PopMoveManager):
        self.pop_move_manager = pop_move_manager
        return self
    
    def add_pop(self, pop: Pop):
        self._instance.pops.append(pop)
        return self
    
    def remove_pop(self, pop):
        self.pops.remove(pop)
        return self
    
    def get_pops(self) -> List[Pop]:
        return self.pops
    
    def move_pop(self, pop, x, y):
        self.pop_move_manager.move_pop(pop, x, y)
        return self
    
    def get_pops_at(self, x, y) -> List[Pop]:
        pops = []
        for pop in self.pops:
            if pop.location == (x, y):
                pops.append(pop)
        return pops
    
    def get_pops_within_radius(self, x, y, radius):
        pops = []
        for pop in self.pops:
            if pop.location[0] >= x - radius and pop.location[0] <= x + radius and pop.location[1] >= y - radius and pop.location[1] <= y + radius:
                pops.append(pop)
        return pops
    
    def update(self):
        for pop in self.pops:
            pop.update()
        return self