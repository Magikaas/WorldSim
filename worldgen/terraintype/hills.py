from worldgen.terrain import Terrain

class Hills(Terrain):
    def __init__(self):
        super().__init__('Hills', (128, 128, 0))