from enum import Enum
from abc import ABC, abstractmethod

from obj.item import Item, ItemStack
from obj.worldobj.entity import Entity, EntityState
from obj.worldobj.building import Building

from ai.condition import Condition, OnLocationCondition, HasItemsCondition, BuildingExistsCondition, BlackboardContainsLocationCondition
from ai.blackboard import blackboard as Blackboard

from managers.pop_manager import pop_manager as PopManager

from obj.worldobj.resourcenode import NoResource
from object_types import Location
from utils.logger import Logger

from managers.pop_move_manager import pop_move_manager as PopMoveManagerInstance

class ActionState(Enum):
    INACTIVE = 0
    ACTIVE = 1
    DONE = 2

class Action(ABC):
    def __init__(self, name: str, entity: Entity, parent_action=None):
        # self.logger.debug("Initialising action %s for entity %s" % (name, entity.name))
        self.name = name
        self.parent_action = parent_action
        
        self.logger = Logger("action - %s" % name)
        
        self.pop_state = None
        
        self.conditions = {"prep": [], "post": []}
        
        self.retries = 0
        
        self.state = ActionState.INACTIVE
        
        self.entity = PopManager.get_pop(entity.id)
        
        self.determine_conditions()
        self.determine_actions()
    
    def deactivate(self):
        self.logger.info("Deactivating action %s" % self.name, actor=self.entity)
        self.state = ActionState.INACTIVE
    
    def activate(self):
        self.logger.info("Activating action %s" % self.name, actor=self.entity)
        self.state = ActionState.ACTIVE
    
    def is_active(self):
        return self.state == ActionState.ACTIVE
    
    def reset(self):
        self.logger.info("Resetting action %s" % self.name, actor=self.entity)
        self.state = ActionState.INACTIVE
        self.retries = 0
    
    def finish(self):
        self.logger.info("Finishing action %s" % self.name, actor=self.entity)
        self.state = ActionState.DONE
    
    def is_finished(self):
        return self.state == ActionState.DONE
    
    def execute(self):
        self.retries += 1
        
        # self.logger.debug("Entity %s is executing action %s" % (self.entity.name, self.name))
        
        if not self.is_active() and not self.is_finished() and not self.check_prep_conditions():
            if self.retries > 5:
                if self.check_post_conditions():
                    self.finish()
                    return True
                
                if self.retries > 50:
                    self.logger.error("Failed to execute action %s after %s retries" % (self.name, self.retries), actor=self.entity)
            return False
        
        if self.is_active():
            return self.update()
        
        self.activate()
        
        result = self.start()
        
        if result == True:
            self.finish()
        
        return result
    
    def has_subactions(self):
        return False
    
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
        # self.logger.debug("Updating composite action %s" % self.name)
        
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
    
    def has_subactions(self):
        return len(self.actions) > 0

class MoveAction(Action):
    def __init__(self, entity: Entity, location: Location|str, parent_action: CompositeAction|None = None):
        self.location = location
        
        super().__init__(name="move", entity=entity, parent_action=parent_action)
        
        self.logger.debug("Creating move action to location %s" % str(location), actor=entity)
    
    def determine_conditions(self):
        self.add_prep_condition(OnLocationCondition(entity_id=self.entity.id, location=self.location).invert())
        self.add_post_condition(OnLocationCondition(entity_id=self.entity.id, location=self.location))
    
    def start(self):
        world = self.entity.world
        
        location = self.location
        locations = []
        
        if isinstance(location, str) and location.startswith("resource_location:"):
            locations = Blackboard.get(entity=self.entity, action=self.parent_action, key=location)
            location = None
        
        if locations is not None and len(locations) > 0:
            closest_location = self.entity.world.find_closest_location(self.entity.location, locations, self.entity)
            
            if closest_location is not None:
                location = closest_location
        
        if location is None:
            self.logger.debug("No location found", actor=self.entity)
            return False
        
        destination_tile = world.get_tile(location)
        
        path = world.pathfind(pop=self.entity, target_location=destination_tile.location)
        
        self.logger.debug("Created path from", self.entity.location, "to tile:", destination_tile.location, "with length:", len(path.moves), actor=self.entity)
        
        PopMoveManagerInstance.empty_moves(self.entity)
        
        for move in path.moves:
            PopMoveManagerInstance.move_pop(move)
        
        return False # We need to wait for the pop to move
    
    def update(self):
        move = PopMoveManagerInstance.get_move_for_pop(self.entity)
        
        if move is None:
            self.finish()
            return False

class BuildAction(Action):
    def __init__(self, entity: Entity, building: Building, target_tile, parent_action: CompositeAction|None = None):
        self.building = building
        self.pop_state = EntityState.BUILDING
        self.target_tile = target_tile
        
        super().__init__(name="build", entity=entity, parent_action=parent_action)
    
    def is_done(self):
        return self.entity.state == EntityState.IDLE
    
    def determine_conditions(self):
        if len(self.building.materials) > 0:
            for m in self.building.materials:
                self.add_prep_condition(HasItemsCondition(entity_id=self.entity.id, item=m))
        
        self.add_prep_condition(BuildingExistsCondition(building=self.building, target_tile=self.target_tile).invert())
        self.add_post_condition(BuildingExistsCondition(building=self.building, target_tile=self.target_tile))
    
    def start(self):
        self.logger.info("Building %s with %s" % (self.building.name, ', '.join([item.item.name + "x" + str(item.amount) for item in self.building.materials])), actor=self.entity)
        return False # The building is not built yet
    
    def update(self):
        # TODO: Make building take time
        
        world = self.entity.world
        tile = world.get_tile(self.entity.location)
        
        tile.build(self.building, self.entity)
        
        if self.entity.state == EntityState.IDLE:
            self.finish()
            return True
        
        return False

class LocateResourceAction(Action):
    def __init__(self, entity: Entity, resource: Item, parent_action: CompositeAction|None = None):
        self.resource = resource
        self.closest_tile = None
        
        self.pop_state = EntityState.SEARCHING
        
        super().__init__(name="locate_resource", entity=entity, parent_action=parent_action)
    
    def determine_conditions(self):
        # Check if the blackboard has a location for the resource
        max_distance = int(self.entity.world.width / 4)
        self.add_prep_condition(BlackboardContainsLocationCondition(resource=self.resource, entity_id=self.entity.id, max_distance=max_distance).invert())
        self.add_post_condition(BlackboardContainsLocationCondition(resource=self.resource, entity_id=self.entity.id, max_distance=max_distance))
    
    def start(self):
        world = self.entity.world
        
        resource_tiles = world.find_tiles_with_resource_near(location=self.entity.location, resource_type=self.resource, distance=15)
        
        self.shortest_path_length = 1000
        
        for tile in resource_tiles:
            path = world.pathfind(pop=self.entity, target_location=tile.location)
            
            Blackboard.add_resource_location(resource=self.resource, location=tile.location)
            
            if (len(path.moves) < self.shortest_path_length):
                self.shortest_path_length = len(path.moves)
                self.closest_tile = tile
        
        return self.closest_tile is not None
    
    def update(self):
        closest_tile = self.closest_tile
        world = self.entity.world
        
        search_distance = 5
        
        if closest_tile is not None:
            # Add the tile to the blackboard for later actions
            Blackboard.add_resource_location(resource=self.resource, location=closest_tile.location)
        else:
            while closest_tile is None and search_distance < 45:
                search_distance += 5
                resource_tiles = world.find_tiles_with_resource_near(location=self.entity.location, resource_type=self.resource, distance=search_distance)
                
                for tile in resource_tiles:
                    Blackboard.add_resource_location(resource=self.resource, location=tile.location)
                    
                    path = world.pathfind(pop=self.entity, target_location=tile.location)
                    
                    if (len(path.moves) < self.shortest_path_length) or closest_tile is None:
                        self.shortest_path_length = len(path.moves)
                        closest_tile = tile
            
            if closest_tile is not None:
                Blackboard.add_resource_location(resource=self.resource, location=closest_tile.location)
            else:
                # self.logger.warn("Found no resource tiles for %s near location %s" % (self.resource.name, str(self.entity.location)), actor=self.entity)
                return False
        
        self.closest_tile = closest_tile
        
        self.finish()

class HarvestAction(Action):
    def __init__(self, entity: Entity, amount:int=0, parent_action: CompositeAction|None = None):
        super().__init__(name="harvest", entity=entity, parent_action=parent_action)
        
        self.amount = amount
        self.pop_state = EntityState.GATHERING
    
    def start(self):
        world = self.entity.world
        
        location = self.entity.location
        
        tile = world.get_tile(location)
        
        resourcenode = tile.resourcenode
        
        if type(resourcenode) == type(NoResource()):
            self.logger.warn("No resource node found at location %s" % str(location), actor=self.entity)
            return False
        
        item = resourcenode.harvestable_resource
        
        item_stack = ItemStack(item, self.amount)
        
        PopManager.give_item_to_pop(pop=self.entity, item=item_stack)
    
    def update(self):
        # TODO: Make harvesting take time
        if self.entity.state == EntityState.IDLE:
            self.finish()
            return True
        
        return False

class GatherAction(CompositeAction):
    def __init__(self, entity: Entity, resource: ItemStack, parent_action: CompositeAction|None = None):
        self.resource = resource
        self.pop_state = EntityState.GATHERING
        
        super().__init__(name="gather", entity=entity, parent_action=parent_action)
        
        self.logger = Logger("action - %s" % (self.name))
    
    def determine_conditions(self):
        self.add_prep_condition(HasItemsCondition(entity_id=self.entity.id, item=self.resource).invert())
        self.add_post_condition(HasItemsCondition(entity_id=self.entity.id, item=self.resource))
    
    def determine_actions(self):
        item = self.resource.item if isinstance(self.resource, ItemStack) else self.resource
        amount = self.resource.amount if isinstance(self.resource, ItemStack) else self.resource
        
        resource_key = ':'.join(["resource_location", item.category, item.name]) if isinstance(item, Item) else type(item)
        
        self.add_action(LocateResourceAction(entity=self.entity, resource=item, parent_action=self))
        self.add_action(MoveAction(entity=self.entity, location=resource_key, parent_action=self))
        self.add_action(HarvestAction(entity=self.entity, amount=amount, parent_action=self))
    
    def start(self) -> bool:
        return super().start()
    
    def update(self) -> bool:
        return super().update()

class DrinkAction(Action):
    def __init__(self, entity: Entity, parent_action: CompositeAction|None = None):
        super().__init__(name="drink", entity=entity, parent_action=parent_action)
    
    def start(self):
        tile = self.entity.world.get_tile(self.entity.location)
        
        resourcenode = tile.resourcenode
        
        water = resourcenode.harvestable_resource
        
        # self.entity.drink(water)