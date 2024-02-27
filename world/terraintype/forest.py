from world.terrain import Terrain

class Forest(Terrain):
    def __init__(self):
        super().__init__('Forest', colour=(0, 128, 0), speed_multiplier=0.8)