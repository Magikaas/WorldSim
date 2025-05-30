from __future__ import annotations
from typing import TYPE_CHECKING
from enum import Enum

import random

from dataclasses import dataclass, field

from crafting.recipe import Recipe
from managers.pop_move_manager import pop_move_manager as PopMoveManagerInstance
from managers.pop_goal_manager import PopGoalManager

from ..entity import Entity, EntityState

from ai.goal import FoodGoal, BuildGoal, Goal, GuaranteeBasicToolsGoal

from obj.item import Item, ItemStack, Food
from obj.worldobj.building import Hut

from utils.logger import Logger

from managers.logger_manager import logger_manager

if TYPE_CHECKING:
    import world

class PopGoal(Enum):
    NONE = 0            # nothing to do
    GATHER = 1          # Gather resources
    RETURN_FOUND = 2    # Return with resources
    # TODO: Add more goals, for example:
    # BUILD = 2         # Build something
    # FARM = 3          # Fetch water, plant seeds, harvest crops
    # HUNT = 4          # Hunt animals

class Pop(Entity):
    world: world.World
    
    def __init__(self, name, location, world, age=0, role='worker', health=100, food=100, water=100, state=EntityState.IDLE, speed=1):
        super().__init__(name, location, world, age, role, health, food, water, state, speed)
        self.carry_weight = 10
        self.colour = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        
        self.inventory = Inventory()
        
        self.path = None
        
        self.pop_goal_manager = PopGoalManager(self)
        
        self.logger = Logger(name, logger_manager)
    
    def initialise_default_goals(self):
        self.add_goal(FoodGoal(entity=self))
        self.add_goal(GuaranteeBasicToolsGoal(entity=self))
    
    def move_to_world(self, world):
        self.world = world
    
    def add_goal(self, goal: Goal):
        self.pop_goal_manager.add_goal(goal)
    
    def get_current_goal(self) -> Goal|None:
        return self.pop_goal_manager.get_current_goal()
    
    def add_item(self, itemstack: ItemStack):
        self.logger.debug("Pop %s is adding %s to inventory" % (self.name, itemstack.item.name))
        self.inventory.add_item(itemstack)
    
    def remove_item(self, itemstack: ItemStack):
        self.inventory.remove_item(itemstack)
    
    def craft(self, recipe: Recipe):
        for material in recipe.materials:
            self.logger.debug("Pop %s used %s to craft %s" % (self.name, material.item.name, recipe.result.item.name))
            self.remove_item(material)
        
        self.logger.debug("Pop %s crafted %s" % (self.name, recipe.result.item.name))
        self.add_item(recipe.result)
    
    def is_dead(self):
        return self.health <= 0
    
    def eat_food(self, food: ItemStack):
        self.logger.debug("Pop %s is eating %s" % (self.name, food.item.name))
        self.inventory.remove_item(ItemStack(food.item, 1))
        
        self.food += food.item.nutrition
    
    def update(self):
        self.pop_goal_manager.perform_goals()
        
        current_goal = self.pop_goal_manager.get_active_foreground_goal()
        
        if not current_goal:
            target_tile_has_no_building = False
            
            while not target_tile_has_no_building:
                build_location = (random.randint(self.location[0] - 10, self.location[0] + 10), random.randint(self.location[1] - 10, self.location[1] + 10))
                if build_location[0] < 0:
                    build_location = (build_location[0] % self.world.width, build_location[1])
                if build_location[1] < 0:
                    build_location = (build_location[0], build_location[1] % self.world.height)
                
                if not self.world.is_land_tile(build_location):
                    build_location = self.world.get_closest_land_tile_location(build_location)
                
                tile = self.world.get_tile(build_location)
                target_tile_has_no_building = not tile.has_building()
            # random_location = (random.randint(0, self.world.width - 1), random.randint(0, self.world.height - 1))
            self.pop_goal_manager.add_goal(BuildGoal(entity=self, building=Hut(), target_location=build_location))
        
        
        # Count down food and water
        if self.food > 0:
            self.food -= 1
            
            if self.food % 25 == 0:
                self.logger.debug("Pop %s food: %s" % (self.name, self.food))
        
        if self.water > 0:
            self.water -= 1
        
        food_threshold = 100
        
        if self.food < food_threshold and self.inventory.has_food():
            best_food = self.inventory.get_best_food_item()
            
            if best_food is not None:
                food_threshold -= best_food.item.nutrition
            
            if self.food < food_threshold:
                self.eat_food(best_food)
        
        # If food or water is empty, reduce health
        # if self.food <= 0:
        #     self.health -= 3
        
        # if self.water <= 0:
        #     self.health -= 5
        
        # If health is empty, pop dies
        if self.health <= 0:
            self.logger.debug("Pop %s has died" % self.name)
            pass
            # self.world.remove_pop(self)
        
        return True

@dataclass
class Inventory:
    items: dict[Item, ItemStack] = field(default_factory=dict)
    logger: Logger = Logger("inventory", logger_manager)
    
    def add_item(self, added_item: ItemStack):
        for item in self.items:
            if item == added_item.item.name:
                self.items[item].amount += added_item.amount
                return
        
        if added_item.item.name not in self.items:
            self.items[added_item.item.name] = added_item

    def remove_item(self, itemstack: ItemStack):
        if itemstack.item.name not in self.items:
            self.logger.error("Attempting to remove an item from inventory that is not present", actor=None)
            return
        
        if self.items[itemstack.item.name].amount < itemstack.amount:
            self.logger.error("Attempting to remove more of an item from inventory than is present", actor=None)
            return
        
        self.items[itemstack.item.name].amount -= itemstack.amount
        self.logger.debug("Removed %s from inventory" % itemstack.item.name, actor=None)
    
    def has_item(self, item):
        return item.name in self.items
    
    def has_food(self):
        for item in self.items.values():
            if issubclass(type(item.item), Food) and item.amount > 0:
                return True
        return False
    
    def get_best_food_item(self) -> ItemStack:
        best_food = None
        for itemstack in self.items.values():
            item = itemstack.item
            if issubclass(type(item), Food) and itemstack.amount > 0:
                if best_food is None or item.nutrition > best_food.item.nutrition:
                    best_food = itemstack
        return best_food
    
    def get_quantity(self, item):
        return self.items[item.name].amount if item.name in self.items else 0

    def __str__(self):
        return str(self.items)