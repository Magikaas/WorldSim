import numpy as np
from worldgen import WorldGenerator, Tile
from .worldobj import AppleTree, Cactus

class World:
    def __init__(self, width, height, seed=None):
        self.width = width
        self.height = height
        self.seed = seed if seed else np.random.randint(0, 10000)
        np.random.seed(self.seed)  # Ensures reproducibility if a seed is provided
        self.terrain = None
        self.temperature = None
        self.biomes = None
        self.resources = None
        self.pops = []
        
        # Initialize the world's layers
        self.generate_terrain()
        self.generate_temperature()
        self.generate_biomes()
        self.initialize_resources()

    def generate_terrain(self):
        # Placeholder for terrain generation logic
        self.terrain = WorldGenerator(seed=self.seed).generate_map((self.height, self.width))

    def generate_temperature(self):
        # Placeholder for temperature generation logic
        self.temperature = WorldGenerator(seed=self.seed + 1).generate_map((self.height, self.width))

    def generate_biomes(self):
        # Placeholder for biome generation logic
        self.biomes = WorldGenerator(seed=self.seed + 2).generate_map((self.height, self.width))
    
    def get_biome_at(self, x, y):
        return self.biomes[x][y]
    
    def get_harvestables(self):
        # Placeholder for getting harvestable resources
        return self.trees
        
    def generate_trees(self):
        for x in range(self.width):
            for y in range(self.height):
                if self.map[x][y].get_biome().get_name() == 'forest':
                    if np.random.randint(0, 100) < self.map[x][y].get_biome().get_tree_spawn_chance():
                        self.trees.append(AppleTree())
                elif self.map[x][y].biome == 'desert':
                    # Lower chance of trees, different types
                    if np.random.randint(0, 100) < self.map[x][y].get_biome().get_tree_spawn_chance():
                        self.trees.append(Cactus())

    def generate_animals(self):
        for x in range(self.width):
            for y in range(self.height):
                if self.map[x][y].biome.supports_animals():
                    # Add animals based on biome
                    self.animals.append(Animal(species='deer', location=(x, y), health=100, food_value=50))
    
    # Generate map 2d array that implements terrain and biome maps and adds trees and animals
    def generate_map(self):
        map = []
        for x in range(self.width):
            row = []
            for y in range(self.height):
                row.append(Tile(terrain=self.terrain[x][y], biome=self.biomes[x][y]))
            map.append(row)
        return self.map


    def initialize_resources(self):
        # Placeholder for initializing resources on the map
        self.resources = np.zeros((self.height, self.width))

    def add_pop(self, pop):
        self.pops.append(pop)

    def update(self):
        # Update the world state for a new simulation step
        for pop in self.pops:
            pop.update()
            # Implement interactions between pops and the world, such as resource consumption

        # Optionally, update resources, weather, or other global factors

    def simulate(self, steps=100):
        for _ in range(steps):
            self.update()
            # Add any additional simulation step logic here
