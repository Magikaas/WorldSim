from dataclasses import dataclass

from managers.item_manager import item_manager as ItemManager

from obj.item import ItemCategory, Tool


@dataclass
class Axe(Tool):
    name: str = "Axe"
    description: str = "A tool used for chopping down trees."
    durability: int = 50
    max_durability: int = durability
    
    category: str = ItemCategory.TOOL
    tool: bool = True