from __future__ import annotations
from typing import Protocol, TYPE_CHECKING, runtime_checkable

if TYPE_CHECKING:
    import ai.blackboard

class Item:
    def __init__(self, name: str="NO NAME ENTERED", description: str="NO DESCRIPTION ENTERED", value: int=0, weight: int=0, protected: bool=False, durability: int=25):
        self.name = name
        self.description = description
        self.value = value
        self.weight = weight
        self.protected = protected
        self.durability = durability
        
        self.category = "general"
        
        self.requires_container = False
    
    def __hash__(self):
        return hash(self.name)

# Not an actual item, but an indicator that this variable's value is on the Blackboard linked to the Action it is used in
class BlackboardItem:
    def __init__(self, key, entity, action):
        self.key = key
        self.entity = entity
        self.action = action
    
    def get_blackboard_value(self):
        blackboard = ai.blackboard.blackboard
        
        return blackboard.get(key=self.key, entity=self.entity, action=self.action)

@runtime_checkable
class Edible(Protocol):
    nutrition = 0

@runtime_checkable
class Potable(Protocol):
    drink_value = 0

@runtime_checkable
class Tool(Protocol):
    durability: int

class Liquid:
    def __init__(self, name: str, description: str, amount: int):
        self.name = name
        self.description = description
        self.amount = amount

class Container:
    def __init__(self, capacity=0, items=None):
        self.capacity = capacity
        self.items = items or []

    def add(self, item):
        if len(self.items) < self.capacity:
            self.items.append(item)
            return True
        return False

    def remove(self, item):
        if item in self.items:
            self.items.remove(item)
            return True
        return False

class ItemContainer(Container):
    pass

class LiquidContainer(Container):
    def __init__(self, capacity=0, contents=None, liquid: Liquid=None):
        super().__init__(capacity)
        self.liquid = liquid
        self.amount = 0

    def add(self, item: Liquid):
        if len(self.items) < self.capacity:
            if isinstance(item, self.liquid):
                self.amount += item.amount
                return True
            self.items.append(item)
            return True
        return False

    def remove(self, item):
        if item in self.items:
            self.items.remove(item)
            return True
        return False

    def __repr__(self):
        return f'<LiquidContainer: {self.items}>'

    def __str__(self):
        return f'<LiquidContainer: {self.items}>'

class ItemStack:
    def __init__(self, item, amount=1):
        self.item = item
        self.amount = amount
    
    def __str__(self) -> str:
        return f'{self.amount} {self.item.name}'
    
    def take(self, amount=1):
        if amount > self.amount:
            amount = self.amount
            self.amount = 0
        else:
            self.amount -= amount
        return ItemStack(self.item, amount)
    
    def add(self, itemstack):
        if itemstack.item == self.item:
            self.amount += itemstack.amount
            return True
        return False

class Food(Item, Edible):
    def __init__(self, name="Food", description="Generic food item.", value=-1, weight=-1, durability=-1):
        super().__init__(name=name, description=description, value=value, weight=weight, durability=durability)
        
        self.category = "food"
        self.edible = True
        self.nutrition = None

class Water(Item, Potable):
    def __init__(self, name="Water", description="A bottle of water.", value=1, weight=1, durability=25):
        super().__init__(name=name, description=description, value=value, weight=weight, durability=durability)
        
        self.category = "drink"
        self.potable = True
        self.drink_value = 10

class Resource(Item):
    def __init__(self, name="Resource", description="A generic resource.", value=1, weight=1, durability=25):
        super().__init__(name=name, description=description, value=value, weight=weight, durability=durability)
        
        self.category = "resource"

class Wood(Resource):
    def __init__(self, name="Wood", description="A piece of wood, useful for crafting and building.", value=1, weight=5, durability=25):
        super().__init__(name=name, description=description, value=value, weight=weight, durability=durability)

class Stone(Resource):
    def __init__(self, name="Stone", description="A piece of stone, useful for crafting and building.", value=1, weight=5, durability=25):
        super().__init__(name=name, description=description, value=value, weight=weight, durability=durability)

class Apple(Food):
    def __init__(self):
        super().__init__(name="Apple", description="A juicy red apple.", value=5, weight=1, durability=10)
        
        self.nutrition = 10
