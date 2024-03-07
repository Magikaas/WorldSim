from abc import ABC, abstractmethod
from typing import List

from obj.worldobj.worldobjecttype import Entity, Building
from ai.condition import Condition, HasItemsCondition, BuildingExistsCondition
from ai.action import BuildAction, GatherResourceAction

class GoalType:
    RANDOM_SEARCH = 0
    RESOURCE_HARVEST = 1
    BUILD = 2

class Goal(ABC):
    def __init__(self, type: GoalType):
        self.type = type
        self.determine_conditions()
    
    def __str__(self):
        return f"Goal: {self.type} {self.target}"
    
    def check_conditions(self):
        for condition in self.conditions:
            if condition.check() == False:
                return False
        return True
    
    @abstractmethod
    def determine_conditions(self): ...

class BuildGoal(Goal):
    def __init__(self, entity: Entity, building: Building, target: tuple):
        super().__init__(type=GoalType.BUILD)
        self.entity = entity
        self.building = building
        self.target = target
        self.conditions = []
    
    def determine_conditions(self):
        self.conditions.append(BuildingExistsCondition(type))
        # TODO: This needs to be done on the Actions linked to this Goal
        # for item in self.building.get_required_items():
        #     self.conditions.append(HasItemsCondition(target=self.entity, items=[item]))
    
    def determine_actions(self):
        actions = []
        
        materials = self.building.materials
        
        for material in materials:
            actions.append(GatherResourceAction(resource=material))
        actions.append(BuildAction(location=self.target, building=self.building))