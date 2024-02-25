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
            self.initialized = True
    
    def set_world(self, world):
        self.world = world
        return self
    
    def move_pop(self, pop, direction: tuple):
        
        x, y = pop.location[0], pop.location[1]
        
        # X
        x = (x + direction[0]) % self.world.width
        
        if x < 0:
            x = self.world.width + x
        
        # Y
        y = (y + direction[1]) % self.world.height
        
        if y < 0:
            y = self.world.height + y
        
        loc = (x, y)
        
        pop.set_location(loc)
        return self