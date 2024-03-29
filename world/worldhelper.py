from world import World

class WorldHelper():
    def __init__(self, world: World):
        self.world = world
    
    def get_world(self):
        return self.world
    
    def set_world(self, world):
        self.world = world
            
    def get_biome_at(self, x, y):
        return self.world.get_biome_at(x, y)
    
    # Useful functions for getting objects in the world
    def get_closest_harvestable(self, x, y, harvest_type):
        harvestables = self.world.get_harvestables()
    
    def render_world(self, filename):
        return self.world.render(filename, scale=5)