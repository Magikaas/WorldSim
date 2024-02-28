from world.terrain import Terrain

class River(Terrain):
    def __init__(self):
        # Light blue color
        super().__init__('River', (0, 255, 255), speed_multiplier=0.2, fertility=2, can_spawn_resource=True)