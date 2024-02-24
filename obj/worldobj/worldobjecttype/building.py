from obj.worldobject import WorldObject, WORLD_OBJECT_TYPE

class Building(WorldObject):
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.type = WORLD_OBJECT_TYPE.BUILDING