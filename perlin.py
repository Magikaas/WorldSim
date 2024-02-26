# world_generation.py

import numpy as np
from noise import pnoise2

class WorldGenerator:
    def __init__(self, width, height, seed):
        self.width = width
        self.height = height
        self.seed = seed
    
    def generate_noise_map(self, scale, offset=0, octaves=6, persistence=0.5, lacunarity=2.0):
        noise_map = [[0] * self.width for i in range(self.height)]
        for i in range(self.width):
            for j in range(self.height):
                noise_value = pnoise2((i + offset) / scale, 
                                      (j + offset) / scale, 
                                      octaves=octaves, 
                                      persistence=persistence, 
                                      lacunarity=lacunarity, 
                                      repeatx=self.width, 
                                      repeaty=self.height, 
                                      base=self.seed)
                noise_map[i][j] = noise_value
        return noise_map

    def generate_world(self):
        elevation_map = self.generate_noise_map(100.0)
        moisture_map = self.generate_noise_map(50.0, offset=1)
        temperature_map = self.generate_noise_map(50.0, offset=2)
        return elevation_map, moisture_map, temperature_map
