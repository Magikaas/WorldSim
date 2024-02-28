class Item():
    def __init__(self, name="NO NAME ENTERED", description="NO DESCRIPTION ENTERED", value=0, weight=0, durability=25, protected=False):
        self.name = name
        self.description = description
        self.value = value
        self.weight = weight
        self.edible = edible
        self.protected = protected
    
    def is_protected(self):
        return self.protected