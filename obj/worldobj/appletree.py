from obj.item import Apple

from .worldobjecttype.tree import Tree
from .worldobjecttype.harvestable import HarvestType

class AppleTree(Tree):
    def __init__(self):
        super().__init__(type='apple', harvest_type=HarvestType.BARE_HANDS)