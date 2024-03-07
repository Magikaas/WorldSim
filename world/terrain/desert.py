from world.terrain import Terrain

class Desert(Terrain):
    def __init__(self):
        super().__init__('Desert', (255, 255, 0), speed_multiplier=0.5, fertility=0.1, can_spawn_resource=True)