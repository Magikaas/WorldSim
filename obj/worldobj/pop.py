from __future__ import annotations

import random

from helpers.popmovemanager import PopMoveManager

from path.popmove import PopMove
from .worldobjecttype.entity import Entity
from .woodresource import WoodResource

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
    PATHING = 512

class Pop(Entity):
    def __init__(self, id, name, location, world, age=0, role='worker', health=100, food=100, water=100, state=PopState.IDLE, speed=1):
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
        
        self.path = None
        
        self.state = PopState.IDLE
    
    def move_to_world(self, world):
        self.world = world
    
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
    
    def set_location(self, location):
        self.location = location
    
    def set_path(self, path):
        self.path = path
        self.state = PopState.MOVING
    
    def has_path(self):
        return self.path is not None
    
    def has_pending_move(self):
        return PopMoveManager().get_move_for_pop(self) is not None
    
    def is_idle(self):
        return self.state == PopState.IDLE
    
    def update(self):
        # Update logic for aging, health changes, skill improvements, etc.
        self.age += 1
        if self.food <= 0:
            self.health -= 1
            
        if self.water <= 0:
            self.health -= 1
        
        if self.health <= 0:
            self.state = PopState.DEAD
            print("Pop %s has died" % self.name)
            return
        
        
        if self.has_pending_move() == False:
            if self.has_path() and len(self.path.moves) > 0:
                self.state = PopState.PATHING
                # Move along the path
                next_move = self.path.moves.pop(0)
                
                if len(self.path.moves) == 0:
                    self.path = None
                
                popmove = next_move
                PopMoveManager().move_pop(popmove=popmove)
            elif self.state == PopState.WANDERING:
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
                    self.state = PopState.IDLE
            else:
                # No moves to handle, no pathing to do, not wandering looking for resources
                self.state = PopState.IDLE
        
        # Update logic for the pop's current state
        if self.state == PopState.IDLE:
            tiles = self.world.find_tiles_with_resourcenodes_near(location=self.location, distance=5, resourcenode_type=WoodResource)
            
            if len(tiles) == 0:
                # If we can't find tiles with nodes nearby, wander around for 5 cycles and search again
                self.state = PopState.WANDERING
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
                return
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