from world.terrain import Terrain

class ShallowCoastalWater(Terrain):
    def __init__(self):
        super().__init__('Shallow Coastal Water', (0, 0, 256), speed_multiplier=0.4)