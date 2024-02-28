from .item import Item

class Wood(Item):
    def __init__(self, name="Wood", description="A piece of wood, useful for crafting and building.", value=1, weight=5, durability=25):
        super().__init__(name, description, value, weight, durability)
        self.set_protected(True)
    
    def get_type(self):
        return "wood"
    
    def set_type(self, type):
        pass