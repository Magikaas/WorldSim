from dataclasses import dataclass, field

from managers.item_manager import item_manager as ItemManager

from obj.item.item import Resource, Tool
from obj.item.items.axe import Axe


@dataclass
class Wood(Resource):
    name: str = "Wood"
    description: str = "A piece of wood, useful for crafting and building."
    value: int = 1
    weight: int = 5
    durability: int = 25
    
    harvest_tool: Tool = field(default_factory=Axe)