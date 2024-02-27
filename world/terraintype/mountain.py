from world.terrain import Terrain

class Mountain(Terrain):
    def __init__(self):
        super().__init__('Mountain', (128, 128, 128), speed_multiplier=0.2)