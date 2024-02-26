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
    
    def generate_pop(self, name=None, location=(0, 0)):
        if name is None:
            name = "Pop %s" % len(self.pops)
        
        pop = Pop(id=len(self.pops), name=name, location=location)
        return pop
    
    def add_pop(self, pop: Pop):
        self.pops.append(pop)
    
    def remove_pop(self, pop):
        self.pops.remove(pop)
    
    def get_pops(self) -> List[Pop]:
        return self.pops
    
    def move_pop(self, pop, x, y):
        self.pop_move_manager.move_pop(pop, x, y)
    
    def get_pops_within_radius(self, x, y, radius):
        pops = []
        for pop in self.pops:
            if pop.location[0] >= x - radius and pop.location[0] <= x + radius and pop.location[1] >= y - radius and pop.location[1] <= y + radius:
                pops.append(pop)
        return pops
    
    def update(self):
        for pop in self.pops:
            pop.update()