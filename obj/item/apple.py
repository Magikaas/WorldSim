from .item import Item

class Apple(Item):
    def __init__(self):
        super().__init__(name="Apple", description="A juicy red apple.", value=5, weight=0.5, edible=True, durability=10)
        self.is_edible = True
        self.food_value = 5
    
    def get_food_value(self):
        return self.food_value
    
    def set_food_value(self, food_value):
        self.food_value = food_value
        return self