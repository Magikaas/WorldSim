from __future__ import annotations
from typing import Protocol, TYPE_CHECKING, runtime_checkable

if TYPE_CHECKING:
    import ai.blackboard

class Item:
    def __init__(self, name="NO NAME ENTERED", description="NO DESCRIPTION ENTERED", value=0, weight=0, protected=False, durability=25):
        self.name = name
        self.description = description
        self.value = value
        self.weight = weight
        self.protected = protected
        self.durability = durability
        
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
        blackboard = ai.blackboard.Blackboard()
        
        return blackboard.get(key=self.key, entity=self.entity, action=self.action)

@runtime_checkable
class Edible(Protocol):
    food_value = 0
    
    def get_food_value(self): ...
    def set_food_value(self, food_value): ...

@runtime_checkable
class Potable(Protocol):
    drink_value = 0
    
    def get_drink_value(self): ...
    def set_drink_value(self, drink_value): ...

@runtime_checkable
class Tool(Protocol):
    durability: int
    
    def get_durability(self): ...
    def set_durability(self, durability): ...

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

class Wood(Item):
    def __init__(self, name="Wood", description="A piece of wood, useful for crafting and building.", value=1, weight=5, durability=25):
        super().__init__(name=name, description=description, value=value, weight=weight, durability=durability)

class Stone(Item):
    def __init__(self, name="Stone", description="A piece of stone, useful for crafting and building.", value=1, weight=5, durability=25):
        super().__init__(name=name, description=description, value=value, weight=weight, durability=durability)

class Apple(Item, Edible):
    def __init__(self):
        super().__init__(name="Apple", description="A juicy red apple.", value=5, weight=0.5, durability=10)
        self.edible = True
        self.food_value = 5
    
    def get_food_value(self):
        return self.food_value
    
    def set_food_value(self, food_value):
        self.food_value = food_value
