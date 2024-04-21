from world.terrain import Terrain
from obj.worldobj.resourcenode import Oak, AppleTree, StoneResource

class Plains(Terrain):
    def __init__(self):
        resources_list = [Oak, AppleTree, StoneResource]
        
        super().__init__('Plains', (0, 255, 0), speed_multiplier=1.0, fertility=1, can_spawn_resource=True, possible_resources=resources_list)