from attr import dataclass


@dataclass
class CraftingStation:
    name: str
    description: str

    def __str__(self) -> str:
        return f'{self.name} ({self.capacity})'