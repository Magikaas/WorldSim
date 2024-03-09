from .woodresource import WoodResource
from .worldobjecttype.harvestable import HarvestType

from obj.item import Wood

class Oak(WoodResource):
    def __init__(self):
        super().__init__(type='oak', harvest_type=HarvestType.AXE, harvestable_resource=Wood)
    
    