from world.terrain import Terrain
from obj.worldobj.resourcenode import StoneResource

class Hills(Terrain):
    def __init__(self):
        resources_list = [StoneResource]
        
        super().__init__('Hills', (128, 128, 0), speed_multiplier=0.8, fertility=0.5, can_spawn_resource=True, possible_resources=resources_list)