import numpy as np
from obj.worldobject import WorldObject

# Enum with different growth speeds for trees
class TreeGrowthSpeed:
    SLOW = 1
    MEDIUM = 2
    FAST = 3
    BOOSTED = 5

# Enum with types of harvest methods
class HarvestType:
    NONE = 'none'
    AXE = 'axe'
    BARE_HANDS = 'bare_hands'
    SCYTHE = 'scythe'
    SICKLE = 'sickle'

class Tree(WorldObject):
    def __init__(self, type, food_value=np.random.randint(25,100), age=np.random.randint(0, 100), max_age=100, growth_speed=TreeGrowthSpeed.MEDIUM, harvest_type=None, harvest_result=None):
        self.type = type
        self.age = age
        self.food_value = food_value
        self.max_food_value = 100
        self.max_age = max_age
        self.growth_speed = growth_speed
        self.harvest_type = harvest_type
    
    def __repr__(self):
        return f'{self.type} tree'
    
    def set_type(self, type):
        self.type = type
    
    def get_type(self):
        return self.type
    
    def set_food_value(self, food_value):
        self.food_value = food_value
    
    def get_food_value(self):
        return self.food_value
    
    def set_growth_speed(self, growth_speed):
        self.growth_speed = growth_speed
    
    def get_growth_speed(self):
        return self.growth_speed
    
    def set_max_age(self, max_age):
        self.max_age = max_age
    
    def get_max_age(self):
        return self.max_age
    
    def set_age(self, age):
        self.age = age
    
    def get_age(self):
        return self.age
    
    def is_harvestable(self):
        return self.food_value > 0 and self.harvest_type is not HarvestType.NONE
    
    def grow(self):
        if self.food_value is None:
            self.food_value = 0
        
        if self.food_value + self.growth_speed < self.max_food_value:
            self.food_value += self.growth_speed
        else:
            self.food_value = self.max_food_value
    
    def harvest(self):
        if self.food_value > 0:
            self.food_value = 0
    
    def is_dead(self):
        return self.age > self.max_age
    
    def age(self):
        self.age += 1