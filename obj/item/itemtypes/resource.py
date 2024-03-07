from ..itemtype import ItemType

class Resource(ItemType):
    def __init__(self, name, desc):
        super().__init__(name, desc)