from world import World

class WorldHelper():
    def __init__(self, world: World):
        self.world = world
    
    # Useful functions for getting objects in the world
    def get_closest_harvestable(self, x, y, harvest_type):
        harvestables = self.world.get_harvestables()
    
    def render_world(self, filename):
        return self.world.render(filename, scale=5)