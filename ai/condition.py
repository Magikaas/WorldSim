from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, TYPE_CHECKING

from obj.item import Item, ItemStack

from managers.pop_manager import pop_manager as PopManager
from managers.logger_manager import logger_manager
from managers.pop_move_manager import pop_move_manager as PopMoveManagerInstance

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

class CombinedConditionType(Enum):
    AND = "AND"
    OR = "OR"

class Condition(ABC):
    def __init__(self, type: str):
        self.type = type
        self.inverted = False
        
        self.failure_consequence = ConditionFailureConsequence.REPEAT
        
        self.logger = Logger(type, logger_manager)
    
    def __str__(self):
        return self.type
    
    def is_opposite_check(self):
        return self.inverted
    
    def check_condition(self):
        if self.inverted:
            self.logger.debug("Inverted condition: %s" % self)
        else:
            self.logger.debug("Condition: %s" % self)
        
        check_outcome = self.check()
        self.logger.debug("%s: %s" % ("yes" if check_outcome else "no", self.outcome_response()))
        return self.inverted is not check_outcome
    
    def invert(self):
        self.inverted = True
        return self
    
    # The conditions that need to be fulfilled for an action to be considered executed or a goal to be considered completed.
    @abstractmethod
    def check(self): ...
    
    @abstractmethod
    def outcome_response(self): ...

class CombinedCondition(Condition):
    def __init__(self, conditions: List[Condition]=[], type: CombinedConditionType = CombinedConditionType.AND):
        super().__init__(type="combined")
        self.conditions = conditions
        self.type = type
        self.inverted = False
    
    @abstractmethod
    def check(self): ...
    
    def __str__(self):
        str_conditions = [str(condition) for condition in self.conditions]
        str_conditions = ", ".join(str_conditions)
        return "CombinedCondition: %s : %s" % (self.type, str_conditions)
    
    def add_condition(self, condition: Condition):
        self.conditions.append(condition)

class AndCondition(CombinedCondition):
    def __init__(self, conditions: List[Condition]=[]):
        super().__init__(conditions, type=CombinedConditionType.AND)
    
    def __str__(self):
        str_conditions = [str(condition) for condition in self.conditions]
        str_conditions = " and ".join(str_conditions)
        return "I want all: %s" % str_conditions
    
    def check(self):
        for condition in self.conditions:
            if condition.check_condition():
                return True
        return False
    
    def add_condition(self, condition: Condition):
        self.conditions.append(condition)
    
    def outcome_response(self):
        responses = []
        for condition in self.conditions:
            if condition.check_condition():
                responses.append(condition.outcome_response())
        
        return "Result: %s" % " and ".join(responses)

class OrCondition(CombinedCondition):
    def __init__(self, conditions: List[Condition]=[]):
        super().__init__(conditions, type=CombinedConditionType.OR)
    
    def __str__(self):
        str_conditions = [str(condition) for condition in self.conditions]
        str_conditions = " or ".join(str_conditions)
        return "I want either: %s" % str_conditions
    
    def check(self):
        for condition in self.conditions:
            if condition.check_condition():
                return True
        return False
    
    def add_condition(self, condition: Condition):
        self.conditions.append(condition)
    
    def outcome_response(self):
        responses = []
        for condition in self.conditions:
            if condition.check_condition():
                responses.append(condition.outcome_response())
        
        return "Result: %s" % " or ".join(responses)

class ExclusiveSelectorCondition(CombinedCondition):
    def __init__(self, conditions: List[Condition]):
        super().__init__(conditions, type=CombinedConditionType.OR)
    
    def __str__(self):
        str_conditions = [str(condition) for condition in self.conditions]
        str_conditions = " or ".join(str_conditions)
        return "I want only one: %s" % str_conditions
    
    def check(self):
        count = 0
        for condition in self.conditions:
            if condition.check_condition():
                count += 1
                if count > 1:
                    return False
        return count == 1
    
    def outcome_response(self):
        responses = []
        for condition in self.conditions:
            if condition.check_condition():
                responses.append(condition.outcome_response())
        
        return "Result: %s" % " and ".join(responses)

class SelectorCondition(Condition):
    def __init__(self, conditions: List[Condition]):
        super().__init__(type="selector")
        self.conditions = conditions
    
    def __str__(self):
        str_conditions = [str(condition) for condition in self.conditions]
        str_conditions = ", ".join(str_conditions)
        return "SelectorCondition: %s" % str_conditions
    
    def check(self):
        for condition in self.conditions:
            if condition.check_condition():
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
    
    def __str__(self):
        return "Am I at %s?" % str(self.location)
    
    def check(self):
        return self.entity.location == self.location
    
    def outcome_response(self):
        return "I am at %s" % str(self.entity.location)

class HasItemsCondition(Condition):
    def __init__(self, entity_id: int, item: ItemStack):
        super().__init__(type="has_items")
        self.entity = PopManager.get_pop(entity_id)
        self.item = item
        
        self.failure_consequence = ConditionFailureConsequence.ABORT
    
    def __str__(self):
        items = [str(item) for item in self.entity.inventory.items.values()]
        items = ", ".join(items)
        
        if len(items) == 0:
            items = "None"
        
        return "Do I own: %s?" % self.item
    
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
                    self.logger.debug("Missing the following items: %s" % ItemStack(itemstack.item, required_items.amount - itemstack.amount))
                    return False
        
        return False
    
    def outcome_response(self):
        do_I_own_item = self.entity.inventory.has_item(self.item.item)
        if do_I_own_item:
            return "I have %s" % self.item
        else:
            return "I don't have %s" % self.item

class BuildingExistsCondition(Condition):
    def __init__(self, building: Building, target_tile: world.tile.Tile):
        super().__init__(type="building_exists")
        self.building = building
        self.target_tile = target_tile
        
        self.failure_consequence = ConditionFailureConsequence.ABORT
    
    def __str__(self):
        building_string = str(self.target_tile.building) if self.target_tile.has_building() else "None"
        return "Is building %s at %s?" % (self.building, building_string)
    
    def check(self):
        if not self.target_tile.has_building():
            return False
        
        building = self.target_tile.building
        
        return building.type == self.building.type
    
    def outcome_response(self):
        if self.target_tile.has_building():
            if self.target_tile.building.type == self.building.type:
                return "Building %s is at %s" % (self.target_tile.building, self.target_tile)
            else:
                self.logger.debug("Building %s is not at %s" % (self.target_tile.building, self.target_tile))
                return "Building %s is not at %s, instead there is %s" % (self.building, self.target_tile, self.target_tile.building)
        else:
            return "Building %s is not at %s" % (self.building, self.target_tile)

class ResourceExistsCondition(Condition):
    def __init__(self, resource: Item, target_tile: world.tile.Tile):
        super().__init__(type="resource_exists")
        self.resource = resource
        self.target_tile = target_tile
    
        self.failure_consequence = ConditionFailureConsequence.ABORT
    
    def __str__(self):
        return "ResourceExistsCondition: %s vs %s" % (self.target_tile.resourcenode, self.resource)
    
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
    
        self.failure_consequence = ConditionFailureConsequence.ABORT
    
    def __str__(self):
        return "Is my %s %s %s?" % (self.property, self.operator.value, self.value)
    
    def check(self):
        result = eval("self.entity." + self.property + " " + self.operator.value + " " + str(self.value))
        return result
    
    def outcome_response(self):
        if self.check():
            return "My %s is %s %s" % (self.property, self.operator.value, self.value)
        else:
            return "My %s is not %s %s" % (self.property, self.operator.value, self.value)

class BlackboardContainsLocationCondition(Condition):
    def __init__(self, resource: Item, entity_id: int, max_distance = 0):
        super().__init__(type="blackboard_contains_location")
        
        self.resource = resource
        self.entity_id = entity_id
        self.max_distance = max_distance
    
        self.entity = PopManager.get_pop(entity_id)
        self.failure_consequence = ConditionFailureConsequence.ABORT
    
    def __str__(self):
        return "Do I know about the location of %s?" % self.resource
    
    def check(self):
        resource_locations = Blackboard.get(key="resource_location:" + str(self.resource if type(self.resource) == str else (self.resource.name if isinstance(self.resource, Item) else None)))
        
        if resource_locations is None or len(resource_locations) == 0:
            return False
        
        if self.max_distance > 0:
            for location in resource_locations:
                distance = self.entity.world.get_distance_between(self.entity.location, location)
                if distance <= self.max_distance:
                    return True
            return False
        
        return False
    
    def outcome_response(self):
        resource_locations = Blackboard.get(key="resource_location:" + str(self.resource if type(self.resource) == str else (self.resource.name if isinstance(self.resource, Item) else None)))
        
        if resource_locations is None or len(resource_locations) == 0:
            return "I don't know where %s is" % self.resource
        
        if self.max_distance > 0:
            for location in resource_locations:
                distance = self.entity.world.get_distance_between(self.entity.location, location)
                if distance <= self.max_distance:
                    return "I know where %s is: %s" % (self.resource, location)
        
        return "I know about the following locations of %s: %s" % (self.resource, resource_locations)

class PopHasMovesCondition(Condition):
    def __init__(self, entity_id: int):
        super().__init__(type="pop_has_moves")
        self.entity = PopManager.get_pop(entity_id)
        
        self.failure_consequence = ConditionFailureConsequence.ABORT
    
    def __str__(self):
        return "Do I (%s) have moves?" % self.entity
    
    def check(self):
        return PopMoveManagerInstance.get_move_for_pop(self.entity) is not None
    
    def outcome_response(self):
        if PopMoveManagerInstance.get_move_for_pop(self.entity) is not None:
            return "I have moves"
        else:
            return "I don't have moves"