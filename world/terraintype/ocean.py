from world.terrain import Terrain

class Ocean(Terrain):
    def __init__(self):
        super().__init__('Ocean', (0, 0, 128), speed_multiplier=0.1, fertility=1, can_spawn_resource=True)