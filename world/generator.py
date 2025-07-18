from concurrent.futures import ProcessPoolExecutor

import os

from turtle import width
from typing import List

# from pynoise.noisemodule import Perlin
# from pynoise.noiseutil import noise_map_plane

import numpy as np
from vnoise import Noise

import random

import numpy as np

from object_types import Location
from world.terrain.terrain import Terrain

from .map_gen_method import MapGenerationMethod


class MapGenerator:
    seed: int = 0
    noise: Noise
    terrain: Noise

    def __init__(self, seed:int|None = None, impl: MapGenerationMethod = MapGenerationMethod.SERIAL):
        if impl not in MapGenerationMethod:
            raise ValueError("Invalid implementation type. Use a valid enum value.")
        if seed is None:
            seed = random.randrange(10**9)
        self.seed = seed
        self.noise = Noise(seed=seed)
        self.terrain = Noise(seed=seed)

        self.impl = impl

        self.logger = None
    
    def guarantee_map_file_path(self):
        if os.path.exists("map") == False:
            os.mkdir("map")
        
        if os.path.exists("map/" + str(self.seed)) == False:
            os.mkdir("map/" + str(self.seed))
    
    def gen_serial_impl(self, size, chunk_size=16, octaves=4, persistence=0.3, lacunarity: int=2, force_new=False, name="Default") -> List[float]:
        map_data = []
        # return map_data
        
        mapfilepath = "map/" + str(self.seed) + "/" + name + "_" + str(size[0]) + "x" + str(size[1]) + ".map"
        
        self.guarantee_map_file_path()
        
        if force_new == False:
            if os.path.exists(mapfilepath) == True:
                with open(mapfilepath, 'r') as reader:
                    map_data = reader.read().split(',')
                    return list(map(float, map_data))

        xrange = np.arange(x * chunk_size, (x + 1) * chunk_size)
        yrange = np.arange(y * chunk_size, (y + 1) * chunk_size)
        
        map_data = self.noise.noise2(x=xrange, y=yrange, octaves=octaves, persistence=persistence, lacunarity=lacunarity*1.111, grid_mode=True)
        
        compressed_map_data = [round(num*10, 1) for num in map_data]
        
        with open(mapfilepath, 'w') as writer:
            writer.write(','.join(map(str, compressed_map_data)))
        
        return compressed_map_data
    
    def gen_concurrent_impl(self, total_map_size, chunk_size=16, octaves=4, persistence=0.3, lacunarity: int=2.22, force_new=False, name="Default") -> List[float]:
        if chunk_size == 0:
            chunk_size = total_map_size[0] // 4
        mapfilepath = "map/" + str(self.seed) + "/" + name + "_" + str(total_map_size[0]) + "x" + str(total_map_size[1]) + ".map"
        
        self.guarantee_map_file_path()

        if force_new == False:
            if os.path.exists(mapfilepath) == True:
                with open(mapfilepath, 'r') as reader:
                    map_data = reader.read().split(',')
                    return list(map(float, map_data))
        
        map_data = [0.0 for _ in range(total_map_size[0] * total_map_size[1])]
        with ProcessPoolExecutor(max_workers=12) as executor:
            threads = []
            for i in range(0, total_map_size[0], chunk_size):
                for j in range(0, total_map_size[1], chunk_size):
                    threads.append(executor.submit(self.generate_map_chunk_async, i, j, chunk_size, octaves, persistence, lacunarity, force_new, name))
            
            thread_count = len(threads)

            finished_threads = 0
            print(f"Processing {thread_count} chunks in parallel...")
            

            for thread in threads:
                result = thread.result()
                chunk_map_data, local_coordinate = result
                self.add_chunk_to_map_data(map_data=map_data, chunk_map_data=chunk_map_data, size=(total_map_size[0], total_map_size[1]), chunk_size=chunk_size, chunk_location=local_coordinate)

                finished_threads += 1

                if finished_threads % 100 == 0 or finished_threads == thread_count:
                    print(f"Processed chunk {finished_threads}/{thread_count}. {round((finished_threads) / thread_count * 100, 2)}% complete.")
        
        compressed_map_data = [round(num, 1) for num in map_data]
        
        with open(mapfilepath, 'w') as writer:
            writer.write(','.join(map(str, compressed_map_data)))
        
        return compressed_map_data
    
    def generate_map(self, total_map_size, chunk_size=16, octaves=4, persistence=0.3, lacunarity: int=2, force_new=False, name="Default") -> List[float]:
        if self.impl == MapGenerationMethod.SERIAL:
            compressed_map_data = self.gen_serial_impl(total_map_size, chunk_size, octaves, persistence, lacunarity, force_new, name)
        elif self.impl == MapGenerationMethod.CONCURRENT:
            compressed_map_data = self.gen_concurrent_impl(total_map_size=total_map_size, chunk_size=chunk_size, octaves=octaves, persistence=persistence, lacunarity=lacunarity, force_new=force_new, name=name)
        else:
            raise ValueError("Unimplemented generation type. Please use another implementation.")
        if not compressed_map_data:
            raise ValueError("Generated map data is empty. Please check the parameters and try again.")
        
        return compressed_map_data
    
    def add_chunk_to_map_data(self, map_data: list[float], chunk_map_data: list[float], size: tuple[int, int], chunk_size: int, chunk_location: Location):
        width, height = size
        
        for local_chunk_y in range(chunk_size):
            for local_chunk_x in range(chunk_size):
                chunk_origin_index = chunk_location[0] * width + chunk_location[1]
                chunk_row_index = chunk_origin_index + local_chunk_y * width
                chunk_global_index = chunk_row_index + local_chunk_x
                
                map_data[chunk_global_index] = chunk_map_data[local_chunk_x][local_chunk_y]
    
    def generate_map_chunk_async(self, x: int, y: int, chunk_size: int, octaves=4, persistence=0.3, lacunarity: int=2, force_new=False, name="Default") -> tuple[List[float], Location]:
        map_data = []
        
        # perlin = Perlin(octaves=octaves, persistence=persistence, lacunarity=lacunarity, seed=self.seed)

        xrange = np.arange(x * chunk_size, (x + 1) * chunk_size)*0.1
        yrange = np.arange(y * chunk_size, (y + 1) * chunk_size)*0.1
        
        map_data = self.noise.noise2(x=xrange, y=yrange, octaves=octaves, persistence=persistence*3, lacunarity=lacunarity, grid_mode=True)
        
        compressed_map_data = [np.round(num*10, 1) for num in map_data]
        
        return compressed_map_data, (x, y)