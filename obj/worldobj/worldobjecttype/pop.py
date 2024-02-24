from .entity import Entity
import numpy as np

class PopState:
    IDLE = 0
    WORKING = 1
    MOVING = 2
    SLEEPING = 4
    EATING = 8
    DEAD = 16
    FIND_FOOD = 32
    FIND_WATER = 64
    FIND_SHELTER = 128
    WANDERING = 256

class Pop(Entity):
    def __init__(self, id, name, location, age=0, role='worker', health=100, food=100, water=100, state=PopState.IDLE):
        super().__init__(id, name, location)
        self.role = role
        self.age = age
        self.health = health
        self.food = food
        self.water = water
        self.state = state
        
        self.wander()
    
    def getStates(self):
        # Pop state is a bitmap of states
        # We need to return a list of states based on current state value
        states = []
        
        for state in PopState.__dict__:
            if self.state & PopState.__dict__[state]:
                states.append(state)
        
        return states
    
    def determineState(self):
        if self.food <= 25:
            self.state = PopState.FIND_FOOD
        elif self.water <= 25:
            self.state = PopState.FIND_WATER
        else:
            self.state = PopState.IDLE
    
    def wander(self):
        self.state = PopState.WANDERING
        return self
    
    def update(self):
        # Update logic for aging, health changes, skill improvements, etc.
        self.age += 1
        if self.food <= 0:
            self.health -= 1
            
        if self.water <= 0:
            self.health -= 1
        
        if self.health <= 0:
            self.state = PopState.DEAD
            return
        
        # self.determineNextTask()
        
        if self.state == PopState.WANDERING:
            xD = 0
            yD = 0
            
            while xD == 0 and yD == 0:
                # Move in a random direction
                xD = np.random.randint(-1, 1)
                if xD == 0:
                    yD = np.random.randint(-1, 1)
            
            self.location = (self.location[0] + xD, self.location[1] + yD)
            
        
        # Update logic for the pop's current state
        if self.state == PopState.IDLE:
            # Do nothing
            pass
        elif self.state == PopState.WORKING:
            # Do work
            pass
        elif self.state == PopState.MOVING:
            # Move to a new location
            pass
        elif self.state == PopState.SLEEPING:
            # Rest
            pass
        elif self.state == PopState.EATING:
            # Eat
            pass
        elif self.state == PopState.FIND_FOOD:
            # Find food
            pass
        elif self.state == PopState.FIND_WATER:
            # Find water
            pass
        elif self.state == PopState.FIND_SHELTER:
            # Find shelter
            pass
        elif self.state == PopState.DEAD:
            # Do nothing
            pass
        else:
            # Do nothing
            pass