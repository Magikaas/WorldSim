from dataclasses import dataclass

from obj.item import ItemStack


@dataclass
class Recipe():
    materials: list[ItemStack]
    result: ItemStack
    
    def __str__(self) -> str:
        materials_string = ", ".join([f'{material.amount} {material.item.name}' for material in self.materials])
        return f'{materials_string} => {self.result}'