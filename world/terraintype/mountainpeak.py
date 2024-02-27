from world.terrain import Terrain

class MountainPeak(Terrain):
    def __init__(self):
        super().__init__('Mountain Peak', (255, 255, 255), speed_multiplier=0.1)