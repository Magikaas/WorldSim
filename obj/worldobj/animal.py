import numpy as np
from world.worldobject import WorldObject

class Animal(WorldObject):
    def __init__(self, species, location, health, food_value):
        self.species = species
        self.location = location
        self.health = health
        self.food_value = food_value
        self.age = 0
        self.max_age = 100
        self.dead = False
        self.reproduction_rate = 0.5
        self.hunger_rate = 0.5
        self.food_value = 50
        self.food = np.random.randn(25, 100)

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