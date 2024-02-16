class Biome():
    def __init__(self, name, colour):
        self.name = name
        self.colour = colour
        self.tree_density = 0.5
    
    def get_name(self):
        return self.name
    
    def set_name(self, name):
        self.name = name
        return self
    
    def get_colour(self):
        return self.colour
    
    def set_colour(self, colour):
        self.colour = colour
        return self
    
    def get_tree_density(self):
        return self.tree_density
    
    def set_tree_density(self, tree_density):
        self.tree_density = tree_density
        return self
    
    def get_tree_spawn_chance(self):
        return self.tree_density * 100