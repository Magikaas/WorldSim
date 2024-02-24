class WORLD_OBJECT_TYPE:
    ITEM = 0
    CONTAINER = 1
    BUILDING = 2
    ANIMAL = 3
    TREE = 4
    RESOURCE = 5

class WorldObject():
    def __init__(self, name, description):
        self.name = name
        self.description = description
        # self.location = location
        # self.weight = weight
        # self.is_open = False
        # self.contents = []
        # self.is_container = False
        # self.is_locked = False
        # self.is_locked_with_key = False