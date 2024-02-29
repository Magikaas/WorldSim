from .woodresource import WoodResource
from .worldobjecttype.harvestable import HarvestType

class Cactus(WoodResource):
    def __init__(self):
        super().__init__(type='cactus', harvest_type=HarvestType.SICKLE)