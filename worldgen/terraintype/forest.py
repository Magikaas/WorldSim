from worldgen.terrain import Terrain

class Forest(Terrain):
    def __init__(self):
        super().__init__('Forest', colour=(0, 128, 0))