class Item():
    def __init__(self, name="NO NAME ENTERED", description="NO DESCRIPTION ENTERED", value=0, weight=0, durability=25, edible=False, protected=False):
        self.name = name
        self.description = description
        self.value = value
        self.weight = weight
        self.edible = edible
        self.protected = protected
    
    def get_name(self):
        return self.name
    
    def set_name(self, name):
        self.name = name
    
    def get_description(self):
        return self.description
    
    def set_description(self, description):
        self.description = description
    
    def get_value(self):
        return self.value
    
    def set_value(self, value):
        self.value = value
    
    def get_weight(self):
        return self.weight
    
    def set_weight(self, weight):
        self.weight = weight
    
    def is_edible(self):
        return self.edible
    
    def set_edible(self, edible):
        self.edible = edible
    
    def get_durability(self):
        return self.durability
    
    def set_durability(self, durability):
        self.durability = durability
    
    def is_protected(self):
        return self.protected
    
    def set_protected(self, protected):
        self.protected = protected