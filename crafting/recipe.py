from dataclasses import dataclass

from crafting.crafting_station import CraftingStation
from obj.item import ItemStack
from obj.item.item import Tool


@dataclass
class Recipe():
    materials: list[ItemStack]
    result: ItemStack
    required_station: CraftingStation | None = None
    required_tool: Tool | None = None
    crafting_time: int = 0
    
    def __str__(self) -> str:
        materials_string = ", ".join([f'{material.amount} {material.item.name}' for material in self.materials])
        return f'{materials_string} => {self.result}'
    
    def requires_station(self) -> bool:
        return self.required_station is not None
    
    def requires_tool(self) -> bool:
        return self.required_tool is not None