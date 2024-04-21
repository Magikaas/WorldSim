from world.terrain import Terrain
from obj.worldobj.resourcenode import Oak, AppleTree, StoneResource

class Forest(Terrain):
    def __init__(self):
        resources_list = [Oak, AppleTree, StoneResource]
        
        super().__init__('Forest', colour=(0, 128, 0), speed_multiplier=0.8, fertility=2, can_spawn_resource=True, possible_resources=resources_list)