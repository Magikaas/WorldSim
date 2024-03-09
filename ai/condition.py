from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING

from obj.worldobj.worldobjecttype import Entity, Building
from obj.item import Item, ItemStack

if TYPE_CHECKING:
    import world
    import world.tile

class Condition(ABC):
    def __init__(self, type: str):
        self.type = type
    
    def is_opposite_check(self):
        return self.inverted
    
    def check_condition(self):
        return self.inverted is not self.check()
    
    def inverted(self):
        self.inverted = True
        return self
    
    # The conditions that need to be fulfilled for an action to be considered executed or a goal to be considered completed.
    @abstractmethod
    def check(self): ...

class OnLocationCondition(Condition):
    def __init__(self, entity: Entity, location: world.tile.Tile):
        super().__init__(type="move")
        self.entity = entity
        self.location = location
    
    def check(self):
        return self.entity.location == self.location

class HasItemsCondition(Condition):
    def __init__(self, entity: Entity, items: List[ItemStack]):
        super().__init__(type="has_items")
        self.entity = entity
        self.items = items
        self.remaining_items = []
    
    def get_remaining_items(self):
        return self.remaining_items
    
    def check(self):
        target_inventory = self.entity.get_inventory()
        target_items = target_inventory.get_items()
        
        items_to_check = self.items
        
        items_to_get = []
        
        check_attempts = 0
        
        while len(items_to_check) > 0:
            if check_attempts > 100:
                print("Something went wrong checking for items in " + self.entity.name + "'s inventory for these items: " + str(self.items))
                break
            
            check_attempts += 1
            
            for check_item in items_to_check:
                if len(target_items) == 0:
                    items_to_get = items_to_check
                    items_to_check = []
                else:
                    for itemstack in target_items:
                        # Does the target have the item in its inventory?
                        if itemstack.item == check_item.item:
                            remaining_amount = itemstack.amount - check_item.amount
                            
                            # Does the target have enough of the item in its inventory?
                            if remaining_amount >= 0:
                                # Not enough items, but we do have some
                                item_to_get = ItemStack(item=itemstack.item, amount=remaining_amount)
                                items_to_get.append(item_to_get)
                            
                            items_to_get.remove(itemstack)

                        if len(items_to_get) == 0:
                            print("Entity %s has %s %s" % (self.entity.name, check_item.amount, check_item.item.name))
                            return True
        
        self.remaining_items = items_to_get
        
        print("Entity %s does not have %s %s" % (self.entity.name, check_item.amount, check_item.item.name))
        
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
