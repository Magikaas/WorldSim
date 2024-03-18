from abc import ABC

class EntityState:
    IDLE = "idle"
    WORKING = "working"
    SLEEPING = "sleeping"
    EATING = "eating"
    DEAD = "dead"
    FIND_FOOD = "find_food"
    FIND_WATER = "find_water"
    FIND_SHELTER = "find_shelter"
    WANDERING = "wandering"
    PATHING = "pathing"
    FARMING = "farming"
    GATHERING = "gathering"
    HARVESTING = "harvesting"
    BUILDING = "building"
    SEARCHING = "searching"

class Entity(ABC):
    def __init__(self, id, name, location, world, age, role, health, food, water, state, speed):
        self.id = id
        self.name = name
        self.location = location
        self.world = world
        self.age = age
        self.role = role
        self.health = health
        self.food = food
        self.water = water
        self.state = state
        self.previous_state = state
        self.speed = speed