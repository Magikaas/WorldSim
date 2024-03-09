from abc import ABC

class EntityState:
    IDLE = 0
    WORKING = 1
    MOVING = 2
    SLEEPING = 3
    EATING = 4
    DEAD = 5
    FIND_FOOD = 6
    FIND_WATER = 7
    FIND_SHELTER = 8
    WANDERING = 9
    PATHING = 10
    FARMING = 11
    GATHERING = 12
    BUILDING = 13
    SEARCHING = 14

class Entity(ABC):
    def __init__(self, id, name, location, world):
        self.id = id
        self.name = name
        self.location = location
        self.world = world