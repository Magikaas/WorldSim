from world.terrain import Terrain

class Plains(Terrain):
    def __init__(self):
        # Light green color
        super().__init__('Plains', (0, 255, 0), speed_multiplier=1.0, fertility=1, can_spawn_resource=True)