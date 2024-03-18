from enum import Enum
from abc import ABC, abstractmethod

from obj.item import Item, ItemStack
from obj.worldobj.entity import Entity, EntityState
from obj.worldobj.building import Building

from ai.condition import Condition, OnLocationCondition, HasItemsCondition, BuildingExistsCondition, BlackboardContainsLocationCondition
from ai.blackboard import Blackboard

import managers.pop_manager

from utils.logger import Logger

from managers.pop_move_manager import PopMoveManager

class ActionState(Enum):
    INACTIVE = 0
    ACTIVE = 1
    DONE = 2

class Action(ABC):
    def __init__(self, name: str, entity: Entity, parent_action=None):
        # self.logger.log("Initialising action %s for entity %s" % (name, entity.name))
        self.name = name
        self.parent_action = parent_action
        
        self.logger = Logger(name)
        
        self.pop_state = None
        
        self.conditions = {"prep": [], "post": []}
        
        self.retries = 0
        
        self.state = ActionState.INACTIVE
        
        self.pop_manager = managers.pop_manager.PopManager()
        self.entity = self.pop_manager.get_pop(entity.id)
        
        self.determine_conditions()
        self.determine_actions()
    
    def deactivate(self):
        self.logger.log("Deactivating action %s" % self.name)
        self.state = ActionState.INACTIVE
    
    def activate(self):
        self.logger.log("Activating action %s" % self.name)
        self.state = ActionState.ACTIVE
    
    def is_active(self):
        return self.state == ActionState.ACTIVE
    
    def finish(self):
        self.logger.log("Finishing action %s" % self.name)
        self.state = ActionState.DONE
    
    def is_finished(self):
        return self.state == ActionState.DONE
    
    def execute(self):
        self.retries += 1
        
        # self.logger.log("Entity %s is executing action %s" % (self.entity.name, self.name))
        
        if not self.check_prep_conditions():
            if self.retries > 5:
                self.logger.log("Entity %s failed to execute action %s after %s retries" % (self.entity.name, self.name, self.retries))
                
                if self.check_post_conditions():
                    self.finish()
                    return True
                
                return False
            return False
        
        if self.is_active():
            return self.update()
        
        self.activate()
        
        prev_pop_state = self.entity.state
        
        if self.pop_state is not None:
            self.entity.set_state(self.pop_state)
        
        result = self.start()
        
        self.entity.set_state(prev_pop_state)
        
        result = result and self.check_post_conditions()
        
        if result == True: 
            self.finish()
        
        return result
    
    def has_subactions(self):
        return len(self.actions) > 0
    
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
        self.conditions["prep"].append(condition)
    
    def add_post_condition(self, condition: Condition):
        self.conditions["post"].append(condition)
    
    def determine_actions(self):
        pass
    
    def determine_conditions(self):
        pass
    
    @abstractmethod
    def start() -> bool: ...
    
    @abstractmethod
    def update(self) -> bool: ...

class CompositeAction(Action):
    actions: list[Action]
    
    def __init__(self, name: str, entity: Entity, parent_action=None):
        self.actions = []
        
        super().__init__(name=name, entity=entity, parent_action=parent_action)
    
    def add_action(self, action: Action):
        self.actions.append(action)
    
    def start(self) -> bool:
        if not self.is_active():
            self.activate()
        return self.check_post_conditions()
    
    def update(self) -> bool:
        # self.logger.log("Updating composite action %s" % self.name)
        
        result = True
        
        for action in self.actions:
            if action.is_finished():
                continue
            else:
                result = False
            
            if action.is_active():
                action.update()
                
                if action.is_finished():
                    continue
                break
            else:
                return action.execute()
        
        if result:
            self.finish()
        return result

class MoveAction(Action):
    def __init__(self, entity: Entity, location: tuple, parent_action: CompositeAction = None):
        self.location = location
        self.path = None
        
        super().__init__(name="move", entity=entity, parent_action=parent_action)
    
    def determine_conditions(self):
        self.add_prep_condition(OnLocationCondition(entity=self.entity, location=self.location).invert())
        self.add_post_condition(OnLocationCondition(entity=self.entity, location=self.location))
    
    def start(self):
        world = self.entity.world
        
        location = self.location
        locations = []
        
        if isinstance(location, str) and location.startswith("resource_location:"):
            locations = Blackboard().get(entity=self.entity, action=self.parent_action, key=location)
        
        if len(locations) > 0:
            location = self.entity.world.find_closest_location(self.entity.location, locations, self.entity)
        
        if location is None:
            self.logger.log("No location found for " + self.entity.name)
            return False
        
        destination_tile = world.get_tile(location)
        
        path = world.pathfind(pop=self.entity, target_location=destination_tile.location)
        self.path = path
        return True
    
    def update(self):
        if self.path is None:
            return False
        
        if len(self.path.moves) == 0:
            self.finish()
            return False
        
        move = self.path.moves[0]
        
        if move.is_done():
            # self.logger.log("Entity %s moved to %s" % (self.entity.name, move.destination_tile.location))
            PopMoveManager().move_pop_to_tile(pop=move.pop, destination=move.destination_tile)
            self.path.moves = self.path.moves[1:]
            return
        
        move.progress_move()

class BuildAction(Action):
    def __init__(self, entity: Entity, building: Building, parent_action: CompositeAction = None):
        self.building = building
        self.pop_state = EntityState.BUILDING
        
        super().__init__(name="build", entity=entity, parent_action=parent_action)
    
    def is_done(self):
        return self.entity.state == EntityState.IDLE
    
    def determine_conditions(self):
        if len(self.building.materials) > 0:
            for m in self.building.materials:
                self.add_prep_condition(HasItemsCondition(entity=self.entity, item=m))
        
        building_tile = self.entity.world.get_tile(self.entity.location)
        
        self.add_prep_condition(BuildingExistsCondition(building=self.building, location=building_tile).invert())
        self.add_post_condition(BuildingExistsCondition(building=self.building, location=building_tile))
    
    def start(self):
        self.logger.log("Entity %s is building %s" % (self.entity.name, self.building.name))
        return True
    
    def update(self):
        # TODO: Make building take time
        
        world = self.entity.world
        tile = world.get_tile(self.entity.location)
        tile.build(self.building)
        
        if self.entity.state == EntityState.IDLE:
            self.finish()
            return True
        
        return False

class LocateResourceAction(Action):
    def __init__(self, entity: Entity, resource: Item, parent_action: CompositeAction = None):
        self.resource = resource
        self.closest_tile = None
        
        self.pop_state = EntityState.SEARCHING
        
        super().__init__(name="locate_resource", entity=entity, parent_action=parent_action)
    
    def determine_conditions(self):
        # Check if the blackboard has a location for the resource
        self.add_prep_condition(BlackboardContainsLocationCondition(resource=self.resource).invert())
        self.add_post_condition(BlackboardContainsLocationCondition(resource=self.resource))
    
    def start(self):
        world = self.entity.world
        
        resource_tiles = world.find_tiles_with_resource_near(location=self.entity.location, resource_type=self.resource, distance=5)
        
        self.shortest_path_length = 0
        
        for tile in resource_tiles:
            path = world.pathfind(pop=self.entity, target_location=tile.location)
            
            if (len(path.moves) < self.shortest_path_length):
                self.shortest_path_length = len(path.moves)
                self.closest_tile = tile
        
        return True
    
    def update(self):
        closest_tile = self.closest_tile
        world = self.entity.world
        
        search_distance = 5
        
        if closest_tile is not None:
            # Add the tile to the blackboard for later actions
            Blackboard().add_resource_location(resource=self.resource, location=closest_tile.location)
        else:
            while closest_tile is None and search_distance < 125:
                search_distance += 5
                resource_tiles = world.find_tiles_with_resource_near(location=self.entity.location, resource_type=self.resource, distance=search_distance)
                
                for tile in resource_tiles:
                    Blackboard().add_resource_location(resource=self.resource, location=tile.location)
                    
                    path = world.pathfind(pop=self.entity, target_location=tile.location)
                    
                    if (len(path.moves) < self.shortest_path_length) or closest_tile is None:
                        self.shortest_path_length = len(path.moves)
                        closest_tile = tile
            
            if closest_tile is not None:
                Blackboard().add_resource_location(resource=self.resource, location=closest_tile.location)
            else:
                self.logger.log("%s found no resource tiles for %s near location %s" % (self.entity.name, self.resource.name, str(self.entity.location)))
                return False
        
        self.closest_tile = closest_tile
        
        self.finish()

class HarvestAction(Action):
    def __init__(self, entity: Entity, amount:int=0, parent_action: CompositeAction = None):
        super().__init__(name="harvest", entity=entity, parent_action=parent_action)
        
        self.amount = amount
        self.pop_state = EntityState.GATHERING
    
    def start(self):
        world = self.entity.world
        
        location = self.entity.location
        
        tile = world.get_tile(location)
        
        resourcenode = tile.get_resourcenode()
        
        item = resourcenode.get_resource_type()
        
        item_stack = ItemStack(item, self.amount)
        
        managers.pop_manager.PopManager().give_item_to_pop(pop=self.entity, item=item_stack)
    
    def update(self):
        # TODO: Make harvesting take time
        if self.entity.state == EntityState.IDLE:
            self.finish()
            return True
        
        return False

class GatherAction(CompositeAction):
    def __init__(self, entity: Entity, resource: ItemStack, parent_action: CompositeAction = None):
        self.resource = resource
        self.pop_state = EntityState.GATHERING
        
        super().__init__(name="gather", entity=entity, parent_action=parent_action)
    
    def determine_conditions(self):
        self.add_prep_condition(HasItemsCondition(entity=self.entity, item=self.resource).invert())
        self.add_post_condition(HasItemsCondition(entity=self.entity, item=self.resource))
    
    def determine_actions(self):
        item = self.resource.item if isinstance(self.resource, ItemStack) else self.resource
        amount = self.resource.amount if isinstance(self.resource, ItemStack) else self.resource
        
        self.add_action(LocateResourceAction(entity=self.entity, resource=item, parent_action=self))
        self.add_action(MoveAction(entity=self.entity, location="resource_location:" + item.name))
        self.add_action(HarvestAction(entity=self.entity, amount=amount, parent_action=self))
    
    def start(self) -> bool:
        return super().start()
    
    def update(self) -> bool:
        return super().update()

class DrinkAction(Action):
    def __init__(self, entity: Entity, parent_action: CompositeAction = None):
        super().__init__(name="drink", entity=entity, parent_action=parent_action)
        
        self.pop_state = EntityState.DRINKING
    
    def start(self):
        tile = self.entity.world.get_tile(self.entity.location)
        
        resourcenode = tile.get_resourcenode()
        
        water = resourcenode.get_resource_type()
        
        self.entity.drink(water)