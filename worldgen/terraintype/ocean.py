from worldgen.terrain import Terrain

class Ocean(Terrain):
    def __init__(self):
        super().__init__('Ocean', (0, 0, 128))