from .worldobjecttype import ResourceNode

class StoneResource(ResourceNode):
    def __init__(self):
        super().__init__()
        self.name = 'stone'
        self.resource = 'stone'
        self.resource_amount = 1000
        self.resource_rate = 1