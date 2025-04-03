from abc import ABC, abstractmethod
from enum import Enum
from typing import List

from obj.item import ItemStack, Food, Liquid, Water, Axe, Pickaxe
from obj.worldobj.entity import Entity
from obj.worldobj.building import Building
from ai.condition import Condition, BuildingExistsCondition, HasItemsCondition, EntityPropertyCondition, PropertyCheckOperator
from ai.action import Action, CompositeAction, CraftAxeAction, CraftPickaxeAction, MoveAction, BuildAction, GatherAction

from managers.pop_manager import pop_manager as PopManager
from managers.logger_manager import logger_manager

from object_types import Location
from utils.logger import Logger

class GoalType(Enum):
    RANDOM_SEARCH = "Random Search"
    RESOURCE_HARVEST = "Resource Harvest"
    BUILD = "Build"

class GoalPriority(Enum):
    BACKGROUND = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class GoalState(Enum):
    INACTIVE = "Inactive"
    ACTIVE = "Active"
    FULFILLED = "Fulfilled"

class Goal(ABC):
    actions: List[Action]
    
    def __init__(self, type: GoalType):
        self.type = type
        
        self.conditions = {"prep": [], "post": []}
        self.actions = []
        
        self.fulfilled = False
        
        self.logger = Logger(str(type), logger_manager)
        
        self.entity = PopManager.get_pop(self.entity.id)
        
        self.priority = GoalPriority.MEDIUM
        
        self.determine_conditions()
        self.determine_actions()
        
        self.state = GoalState.INACTIVE
        
        self.tries = 0
    
    def reset(self):
        self.fulfilled = False
        self.actions = []
        self.conditions = {"prep": [], "post": []}
        
        self.tries = 0
        
        self.logger.debug("Goal reset.", actor=self.entity)
        
        self.determine_conditions()
        self.determine_actions()
    
    def __str__(self):
        return f"Goal: {self.type}"
    
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
        all_actions_finished = True
        
        self.state = GoalState.ACTIVE
        
        self.logger.debug(f"Executing goal {self}.", actor=self.entity)
        
        actions_string = "|".join([str(action) if not action.is_finished() else '' for action in self.actions])
        inventory_string = "|".join([str(self.entity.inventory.items[item]) for item in self.entity.inventory.items])
        
        self.logger.debug(f"Actions: {actions_string}", actor=self.entity)
        self.logger.debug(f"Inventory: {inventory_string}", actor=self.entity)
        
        for action in self.actions:
            self.logger.debug(f"Checking action {action} : {action.state}.", actor=self.entity)
            
            if not action.is_active() and not action.is_finished() and action.check_post_conditions():
                action.finish()
                self.logger.debug(f"Action {action} finished without execution - Already completed.", actor=self.entity)
                continue
            
            if action.is_active() and action.check_post_conditions():
                self.logger.debug(f"Action {action} finished normally.", actor=self.entity)
                self.tries = 0
                action.finish()
                continue
            
            if action.is_finished():
                if not action.check_post_conditions():
                    self.logger.debug(f"Action {action} finished, but post conditions not met.", actor=self.entity)
                    
                    all_actions_finished = False
                    action.reset()
                    break
                self.logger.debug(f"Action {action} previously finished.", actor=self.entity)
                continue
            
            if action.is_active():
                self.logger.debug(f"Action {action} is active, update it.", actor=self.entity)
                result = action.update()
                if not result:
                    is_not_move_action = not isinstance(action, CompositeAction) or not isinstance(action.get_active_action(), MoveAction)
                    is_not_move_action = is_not_move_action and not isinstance(action, MoveAction)
                    if is_not_move_action:
                        self.tries += 1
            else:
                self.logger.debug(f"Action {action} is not active, start it.", actor=self.entity)
                action.execute()
            
            # Only consider the goal 'failed' if at least one action is still not finished at this point and a new action was not activated this cycle
            if not action.is_finished():
                all_actions_finished = False
                
                if self.tries > 20:
                    self.logger.debug(f"Action {action} failed.", actor=self.entity)
                    self.reset()
                    break
            else:
                continue
            
            break
        
        self.fulfilled = self.is_fulfilled()
        
        if self.fulfilled:
            self.logger.debug("Goal fulfilment status: FULFILLED.", actor=self.entity)
            self.state = GoalState.FULFILLED
        else:
            if all_actions_finished:
                self.logger.debug("Goal fulfilment status: UNFULFILLED_ACTIONS_COMPLETE.", actor=self.entity)
                self.reset()
            else:
                self.logger.debug("Goal fulfilment status: UNFULFILLED_ONGOING.", actor=self.entity)
        
        return self.fulfilled
    
    def can_execute(self):
        if self.is_fulfilled():
            return False
        
        if len(self.actions) == 0:
            self.determine_actions()
            return False
        
        return self.check_prep_conditions()
    
    def is_fulfilled(self):
        for condition in self.conditions["post"]:
            if not condition.check_condition():
                return False
        
        for action in self.actions:
            if not action.is_finished():
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
    def __init__(self, entity: Entity, building: Building, target_location: Location):
        self.entity = entity
        self.building = building
        self.target_location = target_location
        
        super().__init__(type=GoalType.BUILD)
    
    def __str__(self):
        return "build_goal:" + str(self.building)
    
    def determine_conditions(self):
        tile = self.entity.world.get_tile(self.target_location)
        self.add_prep_condition(BuildingExistsCondition(building=self.building, target_tile=tile).invert())
        self.add_post_condition(BuildingExistsCondition(building=self.building, target_tile=tile))
    
    def determine_actions(self):
        materials = self.building.materials
        tile = self.entity.world.get_tile(self.target_location)
        
        for material in materials:
            self.actions.append(GatherAction(entity=self.entity, target_item=material))
        
        self.actions.append(MoveAction(location=self.target_location, entity=self.entity))
        self.actions.append(BuildAction(entity=self.entity, building=self.building, target_tile=tile))

class GatherGoal(Goal):
    def __init__(self, entity: Entity, itemstack: ItemStack):
        self.entity = entity
        self.itemstack = itemstack
        
        super().__init__(type=GoalType.RESOURCE_HARVEST)
    
    def determine_conditions(self):
        self.add_prep_condition(HasItemsCondition(entity_id=self.entity.id, item=self.itemstack).invert())
        self.add_post_condition(HasItemsCondition(entity_id=self.entity.id, item=self.itemstack))

    def determine_actions(self):
        self.actions.append(GatherAction(entity=self.entity, target_item=self.itemstack))

class FoodGoal(Goal):
    def __init__(self, entity: Entity, min_food_value: int = 70):
        self.entity = entity
        self.min_food_value = min_food_value
        
        super().__init__(type=GoalType.RANDOM_SEARCH)
        
        self.priority = GoalPriority.BACKGROUND
    
    def determine_conditions(self):
        self.add_prep_condition(EntityPropertyCondition(entity_id=self.entity.id, property="food", value=self.min_food_value, operator=PropertyCheckOperator.LESS_THAN))
        self.add_post_condition(EntityPropertyCondition(entity_id=self.entity.id, property="food", value=self.min_food_value, operator=PropertyCheckOperator.GREATER_THAN_OR_EQUALS))
    
    def determine_actions(self):
        if self.entity.food < self.min_food_value and len(self.actions) == 0:
            self.actions.append(GatherAction(entity=self.entity, target_item=ItemStack(item=Food(), amount=15 + self.min_food_value - self.entity.food)))

class DrinkGoal(Goal):
    def __init__(self, entity: Entity, min_food_value: int = 70):
        self.entity = entity
        self.itemstack = (Liquid, 50)
        self.min_food_value = min_food_value
        
        super().__init__(type=GoalType.RANDOM_SEARCH)
        
        self.priority = GoalPriority.BACKGROUND
    
    def determine_conditions(self):
        self.add_prep_condition(EntityPropertyCondition(entity_id=self.entity.id, property="water", value=self.min_food_value, operator=PropertyCheckOperator.LESS_THAN))
        self.add_post_condition(EntityPropertyCondition(entity_id=self.entity.id, property="water", value=self.min_food_value, operator=PropertyCheckOperator.GREATER_THAN_OR_EQUALS))
    
    def determine_actions(self):
        if self.entity.water < self.min_food_value:
            self.actions.append(GatherAction(entity=self.entity, target_item=ItemStack(item=Water(), amount=50 + self.min_food_value - self.entity.water)))


####################### HARDCODED CRAFTING ACTIONS #######################

class GuaranteeBasicToolsGoal(Goal):
    def __init__(self, entity: Entity):
        self.entity = entity
        
        super().__init__(type=GoalType.RANDOM_SEARCH)
    
    def determine_conditions(self):
        self.add_prep_condition(HasItemsCondition(entity_id=self.entity.id, item=ItemStack(item=Axe(), amount=1)).invert())
        self.add_prep_condition(HasItemsCondition(entity_id=self.entity.id, item=ItemStack(item=Pickaxe(), amount=1)).invert())
    
    def determine_actions(self):
        self.actions.append(CraftAxeAction(entity=self.entity))
        self.actions.append(CraftPickaxeAction(entity=self.entity))