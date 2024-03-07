from abc import ABC, abstractmethod
from typing import List

from obj.worldobj.worldobjecttype import Entity, Building
from obj.item import ItemStack

from world.tile import Tile

class Condition(ABC):
    def __init__(self, type: str, inverted: bool=False):
        self.type = type
        self.negative = inverted
    
    def is_opposite_check(self):
        return self.negative
    
    def check(self):
        return self.negative is not self.check_condition()
    
    # The conditions that need to be fulfilled for an action to be considered executed or a goal to be considered completed.
    @abstractmethod
    def check_condition(self): ...

class MoveCondition(Condition):
    def __init__(self, entity: Entity, location: Tile):
        super().__init__(type="move")
        self.entity = entity
        self.location = location
    
    def check_condition(self):
        return self.entity.location == self.location

class HasItemsCondition(Condition):
    def __init__(self, target: Entity, items: List[ItemStack]):
        super().__init__(type="has_items")
        self.target = target
        self.items = items
        self.remaining_items = []
    
    def get_remaining_items(self):
        return self.remaining_items
    
    def check_condition(self):
        target_items = self.target.get_items()
        items_to_check = self.items
        
        items_to_get = []
        
        check_attempts = 0
        
        while len(items_to_check) > 0:
            if check_attempts > 100:
                print("Something went wrong checking for items in " + self.target.name + "'s inventory for these items: " + str(self.items))
                break
            
            check_attempts += 1
            
            for check_item in items_to_check:
                for item in target_items:
                    # Does the target have the item in its inventory?
                    if item.item == check_item.item:
                        remaining_amount = item.amount - check_item.amount
                        
                        # Does the target have enough of the item in its inventory?
                        if remaining_amount >= 0:
                            # Not enough items, but we do have some
                            item_to_get = ItemStack(item=item.item, amount=remaining_amount)
                            items_to_get.append(item_to_get)
                        
                        items_to_get.remove(item)

                    if len(items_to_get) == 0:
                        return True
        
        self.remaining_items = items_to_get
        
        return False

class BuildingExistsCondition(Condition):
    def __init__(self, building: Building, location: Tile):
        super().__init__(type="building_exists")
        self.building = building
        self.location = location
    
    def check_condition(self):
        building = self.location.get_building()
        
        if building is None:
            return False
        
        return building.get_type() == self.building.get_type()
