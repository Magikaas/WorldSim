from .container import Container
from .liquid import Liquid

class LiquidContainer(Container):
    def __init__(self, capacity=0, contents=None, liquid: Liquid=None):
        super().__init__(capacity, contents)
        self.liquid = liquid

    def add(self, item):
        if len(self.contents) < self.capacity:
            self.contents.append(item)
            return True
        return False

    def remove(self, item):
        if item in self.contents:
            self.contents.remove(item)
            return True
        return False

    def __repr__(self):
        return f'<LiquidContainer: {self.contents}>'

    def __str__(self):
        return f'<LiquidContainer: {self.contents}>'