class Item():
    def __init__(self, name="NO NAME ENTERED", description="NO DESCRIPTION ENTERED", value=0, weight=0, protected=False, durability=25):
        self.name = name
        self.description = description
        self.value = value
        self.weight = weight
        self.protected = protected
        self.durability = durability

class ItemStack:
    def __init__(self, item, amount=1):
        self.item = item
        self.amount = amount
    
    def take(self, amount=1):
        if amount > self.amount:
            amount = self.amount
            self.amount = 0
        else:
            self.amount -= amount
        return ItemStack(self.item, amount)
    
    def add(self, itemstack):
        if itemstack.item == self.item:
            self.amount += itemstack.amount
            return True
        return False

class BuildingMaterial(Item):
    def __init__(self, name="Building Material", description="A generic building material.", value=1, weight=5, durability=25):
        super().__init__(name=name, description=description, value=value, weight=weight, durability=durability)

class Wood(BuildingMaterial):
    def __init__(self, name="Wood", description="A piece of wood, useful for crafting and building.", value=1, weight=5, durability=25):
        super().__init__(name=name, description=description, value=value, weight=weight, durability=durability)

class Stone(BuildingMaterial):
    def __init__(self, name="Stone", description="A piece of stone, useful for crafting and building.", value=1, weight=5, durability=25):
        super().__init__(name=name, description=description, value=value, weight=weight, durability=durability)

class Apple(Item):
    def __init__(self):
        super().__init__(name="Apple", description="A juicy red apple.", value=5, weight=0.5, durability=10)
        self.edible = True
        self.food_value = 5
    
    def get_food_value(self):
        return self.food_value
    
    def set_food_value(self, food_value):
        self.food_value = food_value