from world.terrain import Terrain

class Unland(Terrain):
    def __init__(self):
        super().__init__('Unland', (0, 0, 0), speed_multiplier=0, fertility=0, can_spawn_resource=False)