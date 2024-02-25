from world.world import World
from obj.worldobj.worldobjecttype.pop import Pop
import numpy as np

def initialize_pops(world, initial_pop_count):
    initial_pops = []
    for i in range(initial_pop_count):
        # Example: Random placement. Adjust logic for specific starting conditions.
        x = np.random.randint(0, world.width)
        y = np.random.randint(0, world.height)
        pop = Pop(id=i, name=f"Pop {i}", location=(x, y))
        # Optionally, set the pop's location or other properties based on world conditions
        initial_pops.append(pop)
    return initial_pops

def initialize_world(seed, width, height, initial_pop_count):
    world = World(seed=seed, width=width, height=height)
    world.pops = initialize_pops(world, initial_pop_count)
    return world

def generate_trees(self):
    for x in range(self.width):
        for y in range(self.height):
            if self.map[x][y].biome == 'forest':
                # Higher chance of trees
                if random_chance_based_on_biome_density():
                    self.trees.append(Tree(type='oak', location=(x, y), food_value=10))
            elif self.map[x][y].biome == 'desert':
                # Lower chance of trees, different types
                if random_chance_based_on_biome_density():
                    self.trees.append(Tree(type='cactus', location=(x, y), food_value=2))

def generate_animals(self):
    for x in range(self.width):
        for y in range(self.height):
            if self.map[x][y].biome.supports_animals():
                # Add animals based on biome
                self.animals.append(Animal(species='deer', location=(x, y), health=100, food_value=50))
