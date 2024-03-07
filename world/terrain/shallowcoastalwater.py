from world.terrain import Terrain

class ShallowCoastalWater(Terrain):
    def __init__(self):
        super().__init__('Shallow Coastal Water', (0, 0, 255), speed_multiplier=0.4, fertility=0.8, can_spawn_resource=True)