from world.terrain import Terrain

class Tundra(Terrain):
    def __init__(self):
        super().__init__('Tundra', (0, 128, 128), speed_multiplier=0.8, fertility=0.4, can_spawn_resource=True)