from abc import ABC, abstractmethod
from typing import List

from obj.worldobj.worldobjecttype import Entity, Building
from ai.condition import Condition, BuildingExistsCondition, HasItemsCondition
from ai.action import MoveAction, BuildAction, GatherAction

class GoalType:
    RANDOM_SEARCH = 0
    RESOURCE_HARVEST = 1
    BUILD = 2

class Goal(ABC):
    def __init__(self, type: GoalType):
        self.type = type
        
        self.conditions = {"prep": [], "post": []}
        self.actions = []
        
        self.determine_conditions()
        self.determine_actions()
    
    def __str__(self):
        return f"Goal: {self.type} {self.target}"
    
    def check_conditions(self):
        for condition in self.conditions:
            if condition.check_condition() == False:
                return False
        return True
    
    def execute(self):
        for action in self.actions:
            action.execute()
        
        return self.check_post_conditions()
    
    def check_prep_conditions(self):
        for condition in self.conditions["prep"]:
            if not condition.check_condition():
                return False
        return True
    
    def check_post_conditions(self):
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
        self.add_prep_condition(BuildingExistsCondition(type).inverted())
        self.add_post_condition(BuildingExistsCondition(type))
    
    def determine_actions(self):
        materials = self.building.materials
        
        for material in materials:
            self.actions.append(GatherAction(resource=material))
        
        self.actions.append(MoveAction(location=self.target_location, entity=self.entity))
        self.actions.append(BuildAction(location=self.target_location, building=self.building))

class GatherGoal(Goal):
    def __init__(self, entity: Entity, itemstack):
        self.entity = entity
        self.itemstack = itemstack
        
        super().__init__(type=GoalType.RESOURCE_HARVEST)
    
    def determine_conditions(self):
        self.add_prep_condition(HasItemsCondition(entity=self.entity, items=[self.itemstack]).inverted())
        self.add_post_condition(HasItemsCondition(entity=self.entity, items=[self.itemstack]))
    
    def determine_actions(self):
        self.actions.append(GatherAction(entity=self.entity, itemstack=self.itemstack))
