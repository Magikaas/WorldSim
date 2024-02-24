from .worldobjecttype.tree import Tree, HarvestType

class Cactus(Tree):
    def __init__(self):
        super().__init__(type='cactus', harvest_type=HarvestType.SICKLE, harvest_result='cactus')