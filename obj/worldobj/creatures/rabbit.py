from obj.worldobj.creatures.animal import Animal


class Rabbit(Animal):
    def __init__(self, location: tuple[int, int], world=None):
        super().__init__(name=f"Rabbit %s" % id, location=location, world=world)
        self.speed = 1.0
        self.colour = (255, 255, 255)
        self.size = (1, 1)
        self.age = 0