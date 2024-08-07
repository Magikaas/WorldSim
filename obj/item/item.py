from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol, TYPE_CHECKING, runtime_checkable

if TYPE_CHECKING:
    import ai.blackboard

class ItemCategory:
    GENERAL = "general"
    TOOL = "tool"
    FOOD = "food"
    DRINK = "drink"
    RESOURCE = "resource"

@dataclass
class Item:
    name: str = "NO NAME ENTERED"
    description: str = "NO DESCRIPTION ENTERED"
    value: int = 0
    weight: int = 0
    protected: bool = False
    
    category: str = ItemCategory.GENERAL
    
    requires_container: bool = False
    
    def __str__(self):
        return self.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        return self.name == other.name

# Not an actual item, but an indicator that this variable's value is on the Blackboard linked to the Action it is used in
@dataclass
class BlackboardItem:
    key: str
    entity: object
    action: object
    
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
class ItemTypeTool(Protocol):
    durability: int

@dataclass
class Tool(Item, ItemTypeTool):
    name: str = "NO TOOL NAME ENTERED"
    description: str = "NO TOOL DESCRIPTION ENTERED"
    durability: int = 0
    max_durability: int = durability
    
    category: str = ItemCategory.TOOL
    tool: bool = True
    
    def use(self):
        self.durability -= 1
    
    def can_use(self):
        return self.durability > 0
    
    def repair(self):
        self.durability = self.max_durability

@dataclass
class BareHands(Tool):
    name: str = "Bare Hands"
    description: str = "Your hands, useful for picking up items and punching things."
    durability: int = 0
    max_durability: int = durability
    
    category: str = ItemCategory.TOOL
    tool: bool = True

@dataclass
class Liquid:
    name: str
    description: str
    amount: int

@dataclass
class Container:
    capacity: int = 0
    items: list[Item] = field(default_factory=list)

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

@dataclass
class LiquidContainer(Container):
    liquid: Liquid = None
    amount: int = 0

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

@dataclass
class ItemStack:
    item: Item
    amount: int = 1
    
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

@dataclass
class Food(Item, Edible):
    name: str = "Any Food"
    description: str = "Any Food Description"
    category: str = ItemCategory.FOOD
    edible: bool = True
    nutrition: int = 0

@dataclass
class Water(Item, Potable):
    name: str = "NO WATER NAME ENTERED"
    description: str = "NO WATER DESCRIPTION ENTERED"
    category: str = ItemCategory.DRINK
    potable: bool = True
    drink_value: int = 0

@dataclass
class Resource(Item):
    name: str = "Any Resource"
    description: str = "Any Resource Description"
    category: str = ItemCategory.RESOURCE
    harvest_tool: Tool = None

@dataclass
class Apple(Food):
    name: str = "Apple"
    description: str = "A juicy red apple."
    value: int = 5
    weight: int = 1
    
    nutrition: int = 10
    
    harvest_tool: Tool = field(default_factory=BareHands)