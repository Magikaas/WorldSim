from __future__ import annotations
from typing import List
from enum import Enum

import random, copy

from managers.pop_move_manager import PopMoveManager
from managers.pop_goal_manager import PopGoalManager

from path.popmove import PopMove
from .entity import Entity, EntityState

from ai.goal import GatherGoal, FoodGoal, BuildGoal

from obj.item import Item, Wood, ItemStack, Container, LiquidContainer
from obj.worldobj.building import Building, Hut

from obj.worldobj.resourcenode import WoodResource

class PopGoal:
    NONE = 0
    GATHER = 1
    RETURN_FOUND = 2

class PopGoal(Enum):
    NONE = 0            # nothing to do
    GATHER = 1          # Gather resources
    RETURN_FOUND = 2    # Return with resources
    # TODO: Add more goals, for example:
    # BUILD = 2         # Build something
    # FARM = 3          # Fetch water, plant seeds, harvest crops
    # HUNT = 4          # Hunt animals

class Pop(Entity):
    def __init__(self, id, name, location, world, age=0, role='worker', health=100, food=100, water=100, state=EntityState.IDLE, speed=1):
        super().__init__(id, name, location, world, age, role, health, food, water, state, speed)
        self.carry_weight = 10
        self.colour = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        
        self.inventory = Inventory()
        
        self.goal = PopGoal.NONE
        
        self.path = None
        
        self.pop_goal_manager = PopGoalManager(self)
    
    def initialise_default_goals(self):
        self.add_goal(FoodGoal(self))
        self.add_goal(BuildGoal(entity=self, building=Hut(), target_location=(0, 0)))
    
    def move_to_world(self, world):
        self.world = world
    
    def getStates(self):
        # Pop state is a bitmap of states
        # We need to return a list of states based on current state value
        states = []
        
        for state in EntityState.__dict__:
            if self.state & EntityState.__dict__[state]:
                states.append(state)
        
        return states
    
    def determineState(self):
        if self.water <= 25:
            self.set_state(EntityState.FIND_WATER)
        elif self.food <= 25:
            self.set_state(EntityState.FIND_FOOD)
        else:
            self.set_state(EntityState.IDLE)
    
    def wander(self, wander_distance: int):
        self.set_state(EntityState.WANDERING)
        self.wander_distance = wander_distance
    
    def add_goal(self, goal: PopGoal):
        self.pop_goal_manager.add_goal(goal)
    
    def set_state(self, state):
        self.previous_state = copy.copy(self.state)
        self.state = state
    
    def set_location(self, location):
        self.location = location
    
    def set_path(self, path):
        if len(path.moves) == 0:
            print("Attempted to add empty path to pop %s" % self.name)
            return
        self.path = path
        self.set_state(EntityState.PATHING)
    
    def has_path(self):
        return self.path is not None
    
    def set_goal(self, goal: PopGoal):
        self.goal = goal
    
    def get_goal(self):
        return self.pop_goal_manager.get_current_goal()
    
    def has_pending_move(self):
        return PopMoveManager().get_move_for_pop(self) is not None
    
    def is_idle(self):
        return self.state == EntityState.IDLE
    
    def get_inventory(self):
        return self.inventory
    
    def add_item(self, itemstack: ItemStack):
        self.inventory.add_item(itemstack)
    
    def update(self):
        # print("Updating pop %s" % (self.name))
        
        self.pop_goal_manager.perform_goals()
        
        return True

class Inventory:
    def __init__(self):
        self.items = {}
    
    def get_items(self) -> dict[Item, ItemStack]:
        return self.items
    
    def add_item(self, added_item: ItemStack):
        for item in self.items:
            if item == added_item.item:
                self.items[item].amount += added_item
                return
        
        if added_item.item not in self.items:
            self.items[added_item.item] = added_item

    def remove_item(self, itemstack: ItemStack):
        if itemstack.item not in self.items:
            print("Attempting to remove an item from inventory that is not present")
            return
        
        if self.items[itemstack.item] < itemstack.amount:
            print("Attempting to remove more of an item from inventory than is present")
            return
        
        self.items[itemstack.item].amount -= itemstack.amount

    def get_quantity(self, item):
        return self.items[item].amount if item in self.items else 0

    def __str__(self):
        return str(self.items)