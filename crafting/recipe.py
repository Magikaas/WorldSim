from dataclasses import dataclass

from obj.item.item import ItemStack


@dataclass
class Recipe():
    materials: list[ItemStack]
    result: ItemStack