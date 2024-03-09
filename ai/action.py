from abc import ABC, abstractmethod
from typing import List

from obj.item import Item, ItemStack
from obj.worldobj.worldobjecttype import Entity, EntityState, Building

from path.popmove import PopMove

from ai.condition import Condition, OnLocationCondition, HasItemsCondition, BuildingExistsCondition
from ai.blackboard import Blackboard

from managers.pop_move_manager import PopMoveManager

class Action(ABC):
    def __init__(self, name: str, entity: Entity, parent_action=None):
        self.name = name
        self.entity = entity
        self.parent_action = parent_action
        
        self.conditions = {"prep": [], "post": []}
        self.actions = []
        
        self.retries = 0
    
    def execute(self):
        self.retries += 1
        
        if self.retries > 5:
            print("Entity %s failed to execute action %s after %s retries" % (self.entity.name, self.name, self.retries))
            return False
        
        if not self.check_prep_conditions():
            return False
        
        prev_pop_state = self.entity.state
        
        if self.pop_state is not None:
            self.entity.state = self.pop_state
        
        result = None
        
        self.determine_actions()
        
        if self.has_subactions():
            result = self.perform_subactions()
        else:
            result = self.perform_action()
        
        self.entity.state = prev_pop_state
        
        return result and self.check_post_conditions()
    
    def has_subactions(self):
        return len(self.actions) > 0
    
    def perform_subactions(self) -> bool:
        # If there are sub-actions on this action, execute these
        if len(self.actions) > 0:
            action = self.actions[0]
            # If the completion conditions for this action are already fulfilled, skip it
            if action.completion_conditions_fulfilled():
                self.actions.shift()
            else:
                success = action.execute()
                self.actions.shift()
                if success == False:
                    print("Entity %s failed to execute a subaction" % self.entity.name)
                    print("Failed subaction: %s" % action.name)
                    return False
        
        return True
    
    def is_done(self):
        if self.has_subactions():
            for action in self.actions:
                if action.is_done() == False:
                    return False
        else:
            return True
    
    def check_prep_conditions(self) -> bool:
        for condition in self.conditions["prep"]:
            if condition.check_condition() == False:
                return False
        return True
    
    def check_post_conditions(self) -> bool:
        for condition in self.conditions["post"]:
            if condition.check_condition() == False:
                return False
        return True
    
    def add_prep_condition(self, condition: Condition):
        self.conditions.prep.append(condition)
    
    def add_post_condition(self, condition: Condition):
        self.conditions.post.append(condition)
    
    def determine_actions(self):
        pass
    
    @abstractmethod
    def perform_action() -> bool: ...

class CompositeAction(Action):
    def __init__(self, name: str, entity: Entity, parent_action=None):
        super().__init__(name=name, entity=entity, parent_action=parent_action)
    
    def add_action(self, action: Action):
        self.actions.append(action)
    
    def perform_action(self) -> bool:
        pass

class MoveAction(Action):
    def __init__(self, entity: Entity, location: tuple, parent_action: CompositeAction = None):
        super().__init__(name="move", entity=entity, parent_action=parent_action)
        
        self.location = location
    
    def determine_conditions(self):
        self.add_prep_condition(OnLocationCondition(entity=self.entity, location=self.location).inverted())
        self.add_post_condition(OnLocationCondition(entity=self.entity, location=self.location))
    
    def perform_action(self):
        world = self.entity.world
        
        location = self.location
        
        if location is None:
            location = Blackboard().get(entity=self.entity, action=self.parent_action, key="resource_location")
        
        destination_tile = world.get_tile(location)
        
        popmove = PopMove(self.entity, destination_tile=destination_tile)
        PopMoveManager().move_pop(popmove=popmove)

class BuildAction(Action):
    def __init__(self, entity: Entity, building: Building, parent_action: CompositeAction = None):
        super().__init__(name="build", entity=entity, parent_action=parent_action)
        
        self.building = building
        self.pop_state = EntityState.BUILDING
    
    def is_done(self):
        return self.entity.state == EntityState.IDLE
    
    def determine_conditions(self):
        if len(self.building.materials) > 0:
            for m in self.building.materials:
                self.add_prep_condition(HasItemsCondition(entity=self.entity, items=[m]))
        
        self.add_prep_condition(BuildingExistsCondition(building=self.building, location=self.entity.location).inverted())
        self.add_post_condition(BuildingExistsCondition(building=self.building, location=self.entity.location))
    
    def perform_action(self):
        world = self.entity.world
        tile = world.get_tile_at(self.entity.location)
        tile.build(self.building)
        
        return True

class LocateResourceAction(Action):
    def __init__(self, entity: Entity, resource: Item, parent_action: CompositeAction = None):
        super().__init__(name="locate_resource", entity=entity, parent_action=parent_action)
        
        self.resource = resource
        self.pop_state = EntityState.SEARCHING
    
    def perform_action(self):
        world = self.entity.world
        
        search_distance = 5
        
        resource_tiles = world.find_tiles_with_resource_near(location=self.entity.location, resource_type=self.resource, distance=search_distance)
        
        shortest_path = 0
        closest_tile = None
        
        for tile in resource_tiles:
            path = world.pathfind(pop=self.entity, target_location=tile.location)
            
            if (len(path) < shortest_path) or closest_tile is None:
                shortest_path = len(path)
                closest_tile = tile
        
        if closest_tile is not None:
            # Add the tile to the blackboard for later actions
            Blackboard().set(entity=self.entity, action=self.parent_action, key="resource_location", value=closest_tile.location)
        else:
            while closest_tile is None and search_distance < 25:
                search_distance += 5
                resource_tiles = world.find_tiles_with_resource_near(location=self.entity.location, resource_type=self.resource, distance=search_distance)
                
                for tile in resource_tiles:
                    path = world.pathfind(pop=self.entity, target_location=tile.location)
                    
                    if (len(path) < shortest_path) or closest_tile is None:
                        shortest_path = len(path)
                        closest_tile = tile
            
            if closest_tile is not None:
                Blackboard().set(entity=self.entity, action=self.parent_action, key="resource_location", value=closest_tile.location)
            else:
                print("No resource tiles found for " + self.entity.name + " near location " + str(self.entity.location))
                return False
        
        return True

class HarvestAction(Action):
    def __init__(self, entity: Entity, amount:int=0, parent_action: CompositeAction = None):
        super().__init__(name="harvest", entity=entity, parent_action=parent_action)
        
        self.amount = amount
        self.pop_state = EntityState.GATHERING
    
    def perform_action(self):
        world = self.entity.world
        
        location = self.entity.location
        
        tile = world.get_tile_at(location)
        
        resourcenode = tile.get_resourcenode()
        
        item = resourcenode.get_resource_type(amount=self.amount)
        
        item_stack = ItemStack(item, self.amount)
        
        self.entity.add_item(item_stack)

class GatherAction(CompositeAction):
    def __init__(self, entity: Entity, itemstack: ItemStack, parent_action: CompositeAction = None):
        super().__init__(name="gather", entity=entity, parent_action=parent_action)
        
        self.itemstack = itemstack
        self.pop_state = EntityState.GATHERING
    
    def determine_actions(self):
        self.add_action(LocateResourceAction(entity=self.entity, resource=self.itemstack.item, parent_action=self))
        self.add_action(MoveAction(entity=self.entity, location=None))
        self.add_action(HarvestAction(entity=self.entity, amount=self.itemstack.amount, parent_action=self))
    
    def perform_action() -> bool:
        pass