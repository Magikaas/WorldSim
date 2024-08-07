from dataclasses import dataclass

from managers.item_manager import item_manager as ItemManager

from obj.item import ItemCategory, Tool


@dataclass
class Pickaxe(Tool):
    name: str = "Pickaxe"
    description: str = "A tool used for mining stone."
    value: int = 10
    weight: int = 5
    durability: int = 50
    max_durability: int = durability
    
    category: str = ItemCategory.TOOL
    tool: bool = True