from obj.item import Apple

from .woodresource import WoodResource
from .worldobjecttype.harvestable import HarvestType

class AppleTree(WoodResource):
    def __init__(self):
        super().__init__(type='apple', harvest_type=HarvestType.BARE_HANDS)