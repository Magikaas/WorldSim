from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING

from obj.item import Item, ItemStack

from obj.worldobj.entity import Entity
from obj.worldobj.building import Building

from utils.logger import Logger

import managers.pop_manager

from .blackboard import Blackboard

if TYPE_CHECKING:
    import world
    import world.tile

class PropertyCheckOperator:
    EQUALS = "=="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_THAN_OR_EQUALS = ">="
    LESS_THAN_OR_EQUALS = "<="

class Condition(ABC):
    def __init__(self, type: str):
        self.type = type
        self.inverted = False
        
        self.pop_manager = managers.pop_manager.PopManager()
        
        self.logger = Logger(type)
    
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
    def __init__(self, entity: Entity, location: world.tile.Tile):
        super().__init__(type="move")
        self.entity = self.pop_manager.get_pop(entity.id)
        self.location = location
    
    def check(self):
        return self.entity.location == self.location

class HasItemsCondition(Condition):
    def __init__(self, entity: Entity, item: List[ItemStack]):
        super().__init__(type="has_items")
        self.entity = self.pop_manager.get_pop(entity.id)
        self.item = item
        self.remaining_items = []
    
    def get_remaining_items(self):
        return self.remaining_items
    
    def check(self):
        target_inventory = self.entity.get_inventory()
        inv_items = target_inventory.get_items()
        
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
    def __init__(self, building: Building, location: world.tile.Tile):
        super().__init__(type="building_exists")
        self.building = building
        self.location = location
    
    def check(self):
        building = self.location.get_building()
        
        if building is None:
            return False
        
        return building.get_type() == self.building.get_type()

class ResourceExistsCondition(Condition):
    def __init__(self, resource: Item, location: world.tile.Tile):
        super().__init__(type="resource_exists")
        self.resource = resource
        self.location = location
    
    def check(self):
        resourcenode = self.location.get_resourcenode()
        
        if resourcenode is None:
            return False
        
        return resourcenode.get_resource_type() == self.resource

class EntityPropertyCondition(Condition):
    def __init__(self, entity: Entity, property: str, value, operator: PropertyCheckOperator = PropertyCheckOperator.EQUALS):
        super().__init__(type="entity_property")
        self.entity = self.pop_manager.get_pop(entity.id)
        self.property = property
        self.value = value
        self.operator = operator
    
    def check(self):
        result = eval("self.entity." + self.property + " " + self.operator + " " + str(self.value))
        return result

class BlackboardContainsLocationCondition(Condition):
    def __init__(self, resource: Item):
        super().__init__(type="blackboard_contains_location")
        
        self.resource = resource
    
    def check(self):
        resource_locations = Blackboard().get(key="resource_location:" + (self.resource if type(self.resource) == str else self.resource.name))
        if resource_locations is None:
            return False
        return len(resource_locations) > 0