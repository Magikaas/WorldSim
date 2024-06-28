from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, TYPE_CHECKING

from obj.item import Item, ItemStack

from managers.pop_manager import pop_manager as PopManager
from managers.logger_manager import logger_manager
from managers.pop_move_manager import pop_move_manager as PopMoveManagerInstance

from obj.worldobj.entity import Entity
from obj.worldobj.building import Building

from object_types import Location
from utils.logger import Logger

from .blackboard import blackboard as Blackboard

if TYPE_CHECKING:
    import world
    import world.tile

class ConditionFailureConsequence(Enum):
    REPEAT = "Repeat"
    ABORT = "Abort"
    CONTINUE = "Continue"

class PropertyCheckOperator(Enum):
    EQUALS = "=="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_THAN_OR_EQUALS = ">="
    LESS_THAN_OR_EQUALS = "<="

class Condition(ABC):
    def __init__(self, type: str):
        self.type = type
        self.inverted = False
        
        self.failure_consequence = ConditionFailureConsequence.REPEAT
        
        self.logger = Logger(type, logger_manager)
    
    def is_opposite_check(self):
        return self.inverted
    
    def check_condition(self):
        return self.inverted is not self.check()
    
    def invert(self):
        self.inverted = True
        return self
    
    def setContext(self, context):
        self.context = context
    
    # The conditions that need to be fulfilled for an action to be considered executed or a goal to be considered completed.
    @abstractmethod
    def check(self): ...

class SelectorCondition(Condition):
    def __init__(self, conditions: List[Condition]):
        super().__init__(type="selector")
        self.conditions = conditions
    
    def check(self):
        for condition in self.conditions:
            if condition.check():
                return True
        return False
    
    def add_condition(self, condition: Condition):
        self.conditions.append(condition)

class OnLocationCondition(Condition):
    def __init__(self, entity_id: int, location: Location|str):
        super().__init__(type="move")
        self.entity = PopManager.get_pop(entity_id)
        self.location = location
        
        self.failure_consequence = ConditionFailureConsequence.ABORT
    
    def check(self):
        return self.entity.location == self.location

class HasItemsCondition(Condition):
    def __init__(self, entity_id: int, item: ItemStack):
        super().__init__(type="has_items")
        self.entity = PopManager.get_pop(entity_id)
        self.item = item
        self.remaining_items = []
    
    def check(self):
        target_inventory = self.entity.inventory
        inv_items = target_inventory.items
        
        required_items = self.item
        
        if not inv_items:
            return False
        
        for item_name in inv_items:
            itemstack = inv_items[item_name]
            if item_name == required_items.item.name:
                if itemstack.amount >= required_items.amount:
                    return True
                else:
                    self.remaining_items.append(ItemStack(itemstack.item, required_items.amount - itemstack.amount))
                    return False
        
        return False

class BuildingExistsCondition(Condition):
    def __init__(self, building: Building, target_tile: world.tile.Tile):
        super().__init__(type="building_exists")
        self.building = building
        self.target_tile = target_tile
        
        self.failure_consequence = ConditionFailureConsequence.ABORT
    
    def check(self):
        if not self.target_tile.has_building():
            return False
        
        building = self.target_tile.building
        
        return building.type == self.building.type

class ResourceExistsCondition(Condition):
    def __init__(self, resource: Item, target_tile: world.tile.Tile):
        super().__init__(type="resource_exists")
        self.resource = resource
        self.target_tile = target_tile
    
    def check(self):
        resourcenode = self.target_tile.resourcenode
        
        if resourcenode is None:
            return False
        
        return resourcenode.harvestable_resource is self.resource

class EntityPropertyCondition(Condition):
    def __init__(self, entity_id: int, property: str, value, operator: PropertyCheckOperator = PropertyCheckOperator.EQUALS):
        super().__init__(type="entity_property")
        self.entity = PopManager.get_pop(entity_id)
        self.property = property
        self.value = value
        self.operator = operator
    
    def check(self):
        result = eval("self.entity." + self.property + " " + self.operator.value + " " + str(self.value))
        return result

class BlackboardContainsLocationCondition(Condition):
    def __init__(self, resource: Item, entity_id: int, max_distance = 0):
        super().__init__(type="blackboard_contains_location")
        
        self.resource = resource
        self.entity_id = entity_id
        self.max_distance = max_distance
    
    def check(self):
        entity = PopManager.get_pop(self.entity_id)
        
        resource_locations = Blackboard.get(key="resource_location:" + str(self.resource if type(self.resource) == str else (self.resource.name if isinstance(self.resource, Item) else None)))
        
        if resource_locations is None or len(resource_locations) == 0:
            return False
        
        if self.max_distance > 0:
            for location in resource_locations:
                distance = entity.world.get_distance_between(entity.location, location)
                if distance <= self.max_distance:
                    return True
            return False
        
        return False

class PopHasMovesCondition(Condition):
    def __init__(self, entity_id: int):
        super().__init__(type="pop_has_moves")
        self.entity = PopManager.get_pop(entity_id)
    
    def check(self):
        return PopMoveManagerInstance.get_move_for_pop(self.entity) is not None