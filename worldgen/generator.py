import os

# worldgen/generator.py
from pynoise.noisemodule import Perlin
from pynoise.noiseutil import noise_map_plane

from pynoise.noiseutil import terrain_gradient
from pynoise.noiseutil import RenderImage

import numpy as np

class WorldGenerator:
    def __init__(self, seed=None):
        self.seed = seed

    def generate_map(self, size, octaves=10, persistence=0.3, lacunarity=3, scale=0.03):
        map_data = np.zeros(size)
        # return map
        
        seed = 123
        
        mapfilepath = "map/" + str(seed) + ".map"
        
        if os.path.exists("map") == False:
            os.mkdir("map")
        
        if os.path.exists(mapfilepath) == True:
            with open(mapfilepath, 'r') as reader:
                map_data = reader.read().split(',')
                return list(map(float, map_data))
        
        perlin = Perlin(octaves=octaves, persistence=persistence, lacunarity=lacunarity, seed=seed)
        
        map_data = noise_map_plane(width=size[0], height=size[1], lower_x=-1, upper_x=6, lower_z=1, upper_z=4, source=perlin)
        
        with open(mapfilepath, 'w') as writer:
            writer.write(','.join(map(str, map_data)))
        
        # gradient = terrain_gradient()
        # render = RenderImage()
        # render.render(size[0], size[1], map, 'terrain.png', gradient)

        return map_data
    
    def generate_heightmap(self, size, octaves=10, persistence=0.3, lacunarity=3.0, scale=0.03):
        return self.generate_map(size, octaves, persistence, lacunarity, scale)
    
    def generate_temperaturemap(self, size, octaves=5, persistence=0.3, lacunarity=3.0, scale=0.03):
        return self.generate_map(size, octaves, persistence, lacunarity, scale)
    
    def generate_biomemap(self, size, octaves=10, persistence=0.3, lacunarity=3.0, scale=0.1):
        return self.generate_map(size, octaves, persistence, lacunarity, scale)