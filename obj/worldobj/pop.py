from __future__ import annotations

import random

from enum import Enum

from managers.pop_move_manager import PopMoveManager

from path.popmove import PopMove
from .worldobjecttype.entity import Entity, EntityState
from .woodresource import WoodResource

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
        super().__init__(id, name, location, world)
        self.role = role
        self.age = age
        self.health = health
        self.food = food
        self.water = water
        self.state = state
        self.speed = speed
        self.carry_weight = 10
        self.colour = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        
        self.inventory = Inventory()
        
        self.goal = PopGoal.NONE
        
        self.path = None
        
        self.state = EntityState.IDLE
    
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
            self.state = EntityState.FIND_WATER
        elif self.food <= 25:
            self.state = EntityState.FIND_FOOD
        else:
            self.state = EntityState.IDLE
    
    def wander(self):
        self.state = EntityState.WANDERING
    
    def set_location(self, location):
        self.location = location
    
    def set_path(self, path):
        if len(path.moves) == 0:
            print("Attempted to add empty path to pop %s" % self.name)
            return
        self.path = path
        self.state = EntityState.PATHING
    
    def has_path(self):
        return self.path is not None
    
    def set_goal(self, goal: PopGoal):
        self.goal = goal
    
    def get_goal(self):
        return self.goal
    
    def has_pending_move(self):
        return PopMoveManager().get_move_for_pop(self) is not None
    
    def is_idle(self):
        return self.state == EntityState.IDLE
    
    def update(self):
        # Update logic for aging, health changes, skill improvements, etc.
        self.age += 1
        if self.food <= 0:
            self.health -= 1
            
        if self.water <= 0:
            self.health -= 1
        
        if self.health <= 0:
            self.state = EntityState.DEAD
            print("Pop %s has died" % self.name)
            return
        
        
        if self.has_pending_move() == False:
            if self.has_path() and len(self.path.moves) > 0:
                # Move along the path
                next_move = self.path.moves.pop(0)
                
                if len(self.path.moves) == 0:
                    self.path = None
                
                popmove = next_move
                PopMoveManager().move_pop(popmove=popmove)
            elif self.state == EntityState.WANDERING:
                if self.wander_distance > 0:
                    xDiff = 0
                    yDiff = 0
                    
                    while xDiff == 0 and yDiff == 0:
                        # Move in a random direction
                        xDiff = random.randint(-1 * self.speed, self.speed)
                        yDiff = random.randint(-1 * self.speed, self.speed)
                    
                    destination_coords = (self.location[0] + xDiff, self.location[1] + yDiff)
                    destination_tile = self.world.get_tile(location=destination_coords)
                    
                    popmove = PopMove(self, destination_tile=destination_tile)
                    PopMoveManager().move_pop(popmove=popmove)
                    self.wander_distance -= 1
                else:
                    self.state = EntityState.IDLE
            else:
                # No moves to handle, no pathing to do, not wandering looking for resources
                if self.get_goal() == EntityState.GATHERING:
                    # Start gathering resources
                    current_tile = self.world.get_tile(self.location)
                    
                    resourcenode = current_tile.get_resourcenode()
                    if resourcenode is not None:
                        self.state = EntityState.HARVESTING
                    else:
                        self.set_goal(PopGoal.NONE)
                        self.state = EntityState.IDLE
                else:
                    self.state = EntityState.IDLE
        
        # Update logic for the pop's current state
        if self.state == EntityState.IDLE:
            tiles = self.world.find_tiles_with_resourcenodes_near(location=self.location, distance=5, resourcenode_type=WoodResource)
            
            if len(tiles) == 0:
                # If we can't find tiles with nodes nearby, wander around for 5 cycles and search again
                self.state = EntityState.WANDERING
                self.wander_distance = 5
            else:
                # We found one or more tiles with resource nodes, figure out which is closest and move toward it
                closest_tile = None
                
                for tile in tiles:
                    if closest_tile is None:
                        closest_tile = tile
                    else:
                        if self.world.get_distance_between(self.location, tile.location) < self.world.get_distance_between(self.location, closest_tile.location):
                            closest_tile = tile
                
                # Move to the closest node
                path = self.world.pathfind(self, closest_tile.location)
                
                self.set_path(path)
                self.set_goal(PopGoal.GATHER, self)
                return
        elif self.state == EntityState.WORKING:
            # Do work
            pass
        elif self.state == EntityState.MOVING:
            # Move to a new location
            pass
        elif self.state == EntityState.SLEEPING:
            # Rest
            pass
        elif self.state == EntityState.EATING:
            # Eat
            pass
        elif self.state == EntityState.FIND_FOOD:
            # Find food
            pass
        elif self.state == EntityState.FIND_WATER:
            # Find water
            pass
        elif self.state == EntityState.FIND_SHELTER:
            # Find shelter
            pass
        elif self.state == EntityState.DEAD:
            # Do nothing
            pass
        elif self.state == EntityState.GATHERING:
            # Harvest resources
            current_tile = self.world.get_tile(self.location)
            
            resourcenode = current_tile.get_resourcenode()
            harvest_result = resourcenode.harvest()
            
            resource = harvest_result[0]
            amount = harvest_result[1]
            
            
        else:
            # Do nothing
            pass

class Inventory:
    def __init__(self):
        # Initialize the inventory with an empty dictionary
        # Keys are item names (or IDs) and values are quantities
        self.items = {}

    def add_item(self, item, quantity=1):
        """Add a specified quantity of an item to the inventory."""
        if item in self.items:
            self.items[item] += quantity  # Increase quantity if item already exists
        else:
            self.items[item] = quantity  # Add new item with specified quantity

    def remove_item(self, item, quantity=1):
        """Remove a specified quantity of an item from the inventory.
           Removes the item entirely if the quantity drops to zero or below."""
        if item in self.items:
            self.items[item] -= quantity
            if self.items[item] <= 0:
                del self.items[item]  # Remove the item if quantity is zero or negative

    def get_quantity(self, item):
        """Return the quantity of the specified item in the inventory."""
        return self.items.get(item, 0)  # Returns 0 if the item is not found

    def __str__(self):
        """String representation for debugging purposes."""
        return str(self.items)