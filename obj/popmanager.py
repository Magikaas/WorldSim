from typing import List
from .worldobj.worldobjecttype.pop import Pop

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
    
    def add_pop(self, pop: Pop):
        self._instance.pops.append(pop)
        return self
    
    def remove_pop(self, pop):
        self.pops.remove(pop)
        return self
    
    def get_pops(self) -> List[Pop]:
        return self.pops
    
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