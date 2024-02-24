from worldgen.terrain import Terrain

class MountainPeak(Terrain):
    def __init__(self):
        super().__init__('Mountain Peak', (255, 255, 255))