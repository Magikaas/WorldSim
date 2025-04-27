from concurrent.futures import ProcessPoolExecutor
import os
from turtle import width
from typing import List

from pynoise.noisemodule import Perlin
from pynoise.noiseutil import noise_map_plane

import random

import numpy as np

from object_types import Location
from world.terrain.terrain import Terrain

class MapGenerator:
    seed: int = 0
    def __init__(self, seed:int|None = None):
        if seed is None:
            seed = random.randrange(10**9)
        self.seed = seed
        
        self.logger = None
    
    def generate_map(self, size, chunk_size=16, octaves=4, persistence=0.3, lacunarity: int=2, force_new=False, name="Default") -> List[float]:
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

    def generate_map_old(self, size, chunk_size=0, octaves=4, persistence=0.3, lacunarity: int=2, force_new=False, name="Default") -> List[float]:
        if chunk_size == 0:
            chunk_size = size[0] // 4
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
        
        map_data = [0.0 for _ in range(size[0] * size[1])]
        with ProcessPoolExecutor(max_workers=12) as executor:
            threads = []
            for i in range(0, size[0], chunk_size):
                for j in range(0, size[1], chunk_size):
                    threads.append(executor.submit(self.generate_map_async, i, j, chunk_size, octaves, persistence, lacunarity, force_new, name))
            
            for thread in threads:
                result = thread.result()
                chunk_map_data, local_coordinate = result
                self.add_chunk_to_map_data(map_data, chunk_map_data, (size[0], size[1]), chunk_size, local_coordinate)
        
        compressed_map_data = [round(num, 1) for num in map_data]
        
        with open(mapfilepath, 'w') as writer:
            writer.write(','.join(map(str, compressed_map_data)))

        return compressed_map_data
    
    def add_chunk_to_map_data(self, map_data: list[float], chunk_map_data: list[float], size: tuple[int, int], chunk_size: int, chunk_location: Location):
        width, height = size
        
        for i in range(chunk_size):
            for j in range(chunk_size):
                x = chunk_location[0] * chunk_size
                y = chunk_location[1] * chunk_size
                
                map_data_index = x + i * height + y + j
                
                map_data[map_data_index] = chunk_map_data[i * chunk_size + j]
    
    def generate_map_async(self, x: int, y: int, chunk_size: int, octaves=4, persistence=0.3, lacunarity: int=2, force_new=False, name="Default") -> tuple[List[float], Location]:
        map_data = []
        
        perlin = Perlin(octaves=octaves, persistence=persistence, lacunarity=lacunarity, seed=self.seed)
        
        map_data = noise_map_plane(width=chunk_size, height=chunk_size, lower_x=-2, upper_x=6, lower_z=-1, upper_z=5, source=perlin, seamless=False)
        
        compressed_map_data = [round(num, 1) for num in map_data]
        
        return compressed_map_data, (x, y)