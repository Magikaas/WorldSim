from .worldobjecttype.tree import Tree
from .worldobjecttype.harvestable import HarvestType

from obj.item.wood import Wood

class Oak(Tree):
    def __init__(self):
        super().__init__(type='oak', harvest_type=HarvestType.AXE, harvestable_resource=Wood)
    
    