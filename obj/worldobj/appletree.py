from .worldobjecttype.tree import Tree, HarvestType
from obj.item import Apple

class AppleTree(Tree):
    def __init__(self):
        super().__init__(type='apple', harvest_type=HarvestType.BARE_HANDS, harvest_result=[Apple()])