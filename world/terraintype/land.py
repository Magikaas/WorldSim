from world.terrain import Terrain

class Land(Terrain):
    def __init__(self):
        super().__init__('Land', (0, 200, 0))