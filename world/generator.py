import os
from typing import List

# worldgen/generator.py
from pynoise.noisemodule import Perlin
from pynoise.noiseutil import noise_map_plane

import random

import numpy as np

from world.terrain.terrain import Terrain

class MapGenerator:
    seed: int = 0
    def __init__(self, seed:int|None = None):
        if seed is None:
            seed = random.randrange(10**9)
        self.seed = seed

    def generate_map(self, size, octaves=4, persistence=0.3, lacunarity: int=3, force_new=False, name="Default") -> List[float]:
        map_data = []
        # return map_data
        
        mapfilepath = "map/" + str(self.seed) + "/" + str(octaves) + "/" + name + "_" + str(size[0]) + "x" + str(size[1]) + ".map"
        if force_new == False:
            if os.path.exists("map") == False:
                os.mkdir("map")
            
            if os.path.exists("map/" + str(self.seed)) == False:
                os.mkdir("map/" + str(self.seed))
            
            if os.path.exists("map/" + str(self.seed) + "/" + str(octaves) + "/") == False:
                os.mkdir("map/" + str(self.seed) + "/" + str(octaves) + "/")
            
            if os.path.exists(mapfilepath) == True:
                with open(mapfilepath, 'r') as reader:
                    map_data = reader.read().split(',')
                    return list(map(float, map_data))
        
        perlin = Perlin(octaves=octaves, persistence=persistence, lacunarity=lacunarity, seed=self.seed)
        
        map_data = noise_map_plane(width=size[0], height=size[1], lower_x=-2, upper_x=6, lower_z=-1, upper_z=5, source=perlin)
        
        compressed_map_data = [round(num, 1) for num in map_data]
        
        with open(mapfilepath, 'w') as writer:
            writer.write(','.join(map(str, compressed_map_data)))

        return compressed_map_data
    
    def generate_heightmap(self, size, octaves=10, persistence=0.3, lacunarity=3):
        return self.generate_map(size, octaves, persistence, lacunarity)
    
    def generate_temperaturemap(self, size, octaves=5, persistence=0.3, lacunarity=3):
        return self.generate_map(size, octaves, persistence, lacunarity)
    
    def generate_biomemap(self, size, octaves=10, persistence=0.3, lacunarity=3):
        return self.generate_map(size, octaves, persistence, lacunarity)