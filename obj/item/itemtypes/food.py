from ..itemtype import ItemType

class Food(ItemType):
    def __init__(self, name, desc, nutrition):
        super().__init__(name, desc)
        self.nutrition = nutrition
    
    def get_nutrition(self):
        return self.nutrition