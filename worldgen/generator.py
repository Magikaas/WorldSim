# worldgen/generator.py
from noise import pnoise2
import numpy as np

class WorldGenerator:
    def __init__(self, seed=None):
        self.seed = seed

    def generate_map(self, size, octaves=10, persistence=0.3, lacunarity=3.0, scale=0.03):
        np.random.seed(self.seed)
        noisemap = np.zeros((size, size))

        for i in range(size):
            for j in range(size):
                noisemap[i, j] = pnoise2(i * scale,
                j * scale,
                octaves=octaves,
                persistence=persistence,
                lacunarity=lacunarity,
                repeatx=1024,
                repeaty=1024,
                base=self.seed)
            # Normalize heightmap to [0, 1]
        noisemap = (noisemap - np.min(noisemap)) / (np.max(noisemap) - np.min(noisemap))
        return noisemap
    
    def generate_heightmap(self, size, octaves=10, persistence=0.3, lacunarity=3.0, scale=0.03):
        return self.generate_map(size, octaves, persistence, lacunarity, scale)
    
    def generate_temperaturemap(self, size, octaves=5, persistence=0.3, lacunarity=3.0, scale=0.03):
        return self.generate_map(size, octaves, persistence, lacunarity, scale)
    
    def generate_biomemap(self, size, octaves=10, persistence=0.3, lacunarity=3.0, scale=0.1):
        return self.generate_map(size, octaves, persistence, lacunarity, scale)