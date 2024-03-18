from abc import ABC, abstractmethod
from typing import List

from obj.item import Item, ItemStack, Edible, Potable
from obj.worldobj.entity import Entity
from obj.worldobj.building import Building
from ai.condition import Condition, BuildingExistsCondition, HasItemsCondition, EntityPropertyCondition, PropertyCheckOperator
from ai.action import Action, MoveAction, BuildAction, GatherAction

import managers.pop_manager

from utils.logger import Logger

class GoalType:
    RANDOM_SEARCH = "Random Search"
    RESOURCE_HARVEST = "Resource Harvest"
    BUILD = "Build"

class Goal(ABC):
    actions: List[Action]
    
    def __init__(self, type: GoalType):
        self.type = type
        
        self.conditions = {"prep": [], "post": []}
        self.actions = []
        
        self.fulfilled = False
        
        self.logger = Logger(str(type))
        
        self.pop_manager = managers.pop_manager.PopManager()
        
        self.entity = self.pop_manager.get_pop(self.entity.id)
        
        self.determine_conditions()
        self.determine_actions()
    
    def __str__(self):
        return f"Goal: {self.type} {self.target}"
    
    def check_prep_conditions(self):
        for condition in self.conditions["prep"]:
            if condition.check_condition() == False:
                return False
        return True
    
    def check_post_conditions(self):
        for condition in self.conditions["post"]:
            if condition.check_condition() == False:
                return False
        return True
    
    def execute(self):
        for action in self.actions:
            if action.is_finished():
                continue
            
            if action.is_active():
                action.update()
            else:
                action.execute()
            
            break
        
        self.fulfilled = self.is_fulfilled()
        
        return self.fulfilled
    
    def can_execute(self):
        if self.is_fulfilled():
            return False
        
        return self.check_prep_conditions()
    
    def is_fulfilled(self):
        for condition in self.conditions["post"]:
            if not condition.check_condition():
                return False
        return True
    
    def add_prep_condition(self, condition: Condition):
        self.conditions["prep"].append(condition)
    
    def add_post_condition(self, condition: Condition):
        self.conditions["post"].append(condition)
    
    @abstractmethod
    def determine_conditions(self): ...
    
    @abstractmethod
    def determine_actions(self): ...

class BuildGoal(Goal):
    def __init__(self, entity: Entity, building: Building, target_location: tuple):
        self.entity = entity
        self.building = building
        self.target_location = target_location
        
        super().__init__(type=GoalType.BUILD)
    
    def determine_conditions(self):
        tile = self.entity.world.get_tile(self.target_location)
        self.add_prep_condition(BuildingExistsCondition(building=self.building, location=tile).invert())
        self.add_post_condition(BuildingExistsCondition(building=self.building, location=tile))
    
    def determine_actions(self):
        materials = self.building.materials
        
        for material in materials:
            self.actions.append(GatherAction(entity=self.entity, resource=material))
        
        self.actions.append(MoveAction(location=self.target_location, entity=self.entity))
        self.actions.append(BuildAction(entity=self.entity, building=self.building))

class GatherGoal(Goal):
    def __init__(self, entity: Entity, itemstack: ItemStack):
        self.entity = entity
        self.itemstack = itemstack
        
        super().__init__(type=GoalType.RESOURCE_HARVEST)
    
    def determine_conditions(self):
        self.add_prep_condition(HasItemsCondition(entity=self.entity, item=self.itemstack).invert())
        self.add_post_condition(HasItemsCondition(entity=self.entity, item=self.itemstack))

    def determine_actions(self):
        self.actions.append(GatherAction(entity=self.entity, resource=self.itemstack))

class FoodGoal(Goal):
    def __init__(self, entity: Entity, min_food_value: int = 70):
        self.entity = entity
        self.min_food_value = min_food_value
        
        super().__init__(type=GoalType.RANDOM_SEARCH)
    
    def determine_conditions(self):
        self.add_prep_condition(EntityPropertyCondition(entity=self.entity, property="food", value=self.min_food_value, operator=PropertyCheckOperator.LESS_THAN))
        self.add_post_condition(EntityPropertyCondition(entity=self.entity, property="food", value=self.min_food_value, operator=PropertyCheckOperator.GREATER_THAN_OR_EQUALS))
    
    def determine_actions(self):
        if self.entity.food < self.min_food_value:
            self.actions.append(GatherAction(entity=self.entity, resource=ItemStack(item=Edible, amount=5 + self.min_food_value - self.entity.food)))

class DrinkGoal(Goal):
    def __init__(self, entity: Entity, min_food_value: int = 70):
        self.entity = entity
        self.itemstack = (Item.Water, 50)
        self.min_food_value = min_food_value
        
        super().__init__(type=GoalType.RANDOM_SEARCH)
    
    def determine_conditions(self):
        self.add_prep_condition(EntityPropertyCondition(entity=self.entity, property="water", value=self.min_food_value, operator=PropertyCheckOperator.LESS_THAN))
        self.add_post_condition(EntityPropertyCondition(entity=self.entity, property="water", value=self.min_food_value, operator=PropertyCheckOperator.GREATER_THAN_OR_EQUALS))
    
    def determine_actions(self):
        if self.entity.water < self.min_food_value:
            self.actions.append(GatherAction(entity=self.entity, resource=ItemStack(item=Potable, amount=50 + self.min_food_value - self.entity.water)))