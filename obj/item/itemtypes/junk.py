from ..itemtype import ItemType

class Junk(ItemType):
    def __init__(self, name, desc, value=0):
        super().__init__(name, desc)
        self.value = value
    
    def get_value(self):
        return self.value