from world.terrain import Terrain

class Plains(Terrain):
    def __init__(self):
        # Light green color
        super().__init__('Plains', (0, 255, 0))