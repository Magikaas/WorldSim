import numpy as np
from ..entity import Entity, EntityState

class Animal(Entity):
    def __init__(self, name, location, world, age=0, role='worker', health=100, food=100, water=100, state=EntityState.IDLE, speed=1):
        super().__init__(name, location, world, age, role, health, food, water, state, speed)
        self.species = "Generic Animal"
        self.hunger_rate = 1
        self.max_age = 100

    def move(self, new_location):
        self.location = new_location

    def eat(self, food):
        self.food += food.food_value

    def reproduce(self):
        if self.food > 100:
            self.food -= 50
            return Animal(species=self.species, location=self.location, health=100, food_value=50)
        return None

    def update(self):
        self.age += 1
        self.food -= self.hunger_rate
        if self.age > self.max_age or self.food <= 0:
            self.dead = True