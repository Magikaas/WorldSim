from world.terrain import Terrain

class Desert(Terrain):
    def __init__(self):
        super().__init__('Desert', (255, 255, 0))