from world.terrain import Terrain

class Tundra(Terrain):
    def __init__(self):
        # Light blue color
        super().__init__('Tundra', (0, 128, 128))