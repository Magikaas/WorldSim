from abc import ABC, abstractmethod

from obj.item import Item
from obj.worldobj.worldobjecttype import Entity, EntityState, Building

from py_trees.composites import Sequence

from path.popmove import PopMove

from ai.condition import MoveCondition, HasItemsCondition, BuildingExistsCondition

from managers.pop_move_manager import PopMoveManager

class Action(ABC):
    def __init__(self, name: str, entity: Entity):
        self.name = name
        self.entity = entity
        self.conditions = []
        self.actions = []
    
    def execute(self):
        if self.has_subactions():
            return self.perform_subactions()
        else:
            return self.perform_action()
    
    def has_subactions(self):
        return len(self.actions) > 0
    
    def perform_subactions(self) -> bool:
        # If there are sub-actions on this action, execute these
        for action in self.actions:
            # If the completion conditions for this action are already fulfilled, skip it
            if action.completion_conditions_fulfilled():
                continue
            else:
                success = action.execute()
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
    
    @abstractmethod
    def perform_action() -> bool: ...

class CompositeAction(Action):
    def __init__(self, name: str, entity: Entity):
        super().__init__(name=name, entity=entity)
    
    def add_action(self, action: Action):
        self.actions.append(action)
    
    def execute(self):
        for action in self.actions:
            action.execute()

class MoveAction(Action):
    def __init__(self, entity: Entity, location: tuple):
        super().__init__(name="move", entity=entity)
        self.location = location
    
    def execute(self):
        world = self.entity.world
        
        destination_tile = world.get_tile(self.location)
        
        popmove = PopMove(self.entity, destination_tile=destination_tile)
        PopMoveManager().move_pop(popmove=popmove)
    
    def determine_conditions(self):
        conditions = []
        
        conditions.append(MoveCondition(entity=self.entity, location=self.location))

class BuildAction(Action):
    def __init__(self, entity: Entity, building: Building):
        super().__init__(name="build", entity=entity)
        
        self.building = building
    
    def execute(self):
        self.entity.state = EntityState.BUILDING
    
    def is_done(self):
        return self.entity.state == EntityState.IDLE
    
    def determine_conditions(self):
        conditions = []
        
        if len(self.building.materials) > 0:
            for m in self.building.materials:
                conditions.append(HasItemsCondition(target=self.entity, items=[m]))
        
        conditions.append(BuildingExistsCondition(building=self.building, location=self.entity.location))
    
    def determine_actions(self):
        actions = []
        
        actions.append(MoveAction(entity=self.entity, location=self.location))
        
        self.actions = actions

class GatherAction(Action):
    def __init__(self, item: Item):
        super().__init__(name="gather")
    
    def execute(self):
        self.entity.state = EntityState.GATHERING