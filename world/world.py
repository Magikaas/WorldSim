from __future__ import annotations

import random
import pygame

from world.terrain import Terrain, TerrainHeight
from world.biome import Biome, Temperature, BiomeType
from world.terraintype import *

from helpers.popmanager import PopManager
from helpers.chunkmanager import ChunkManager

from obj.worldobj import AppleTree, Cactus
from obj.worldobj import Animal

from .generator import WorldGenerator
from .tile import Tile
from .chunk import Chunk

from render.tilerenderer import TileRenderer
from render.renderoutput import RenderOutput

# Longterm TODO: Make singleton possible with multiple 'Worlds'
class World:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(World, cls).__new__(cls)
            
            cls._instance.__init__(**kwargs)
        return cls._instance
    
    def __init__(self):
        # Initialize only if not already initialized
        if not hasattr(self, 'initialized'):  # This prevents re-initialization
            self.initialized = True  # Mark as initialized
            
            self.terrain = None
            self.temperature = None
            self.biomes = None
            self.chunk_manager = ChunkManager(world=self)
            # self.tiles_per_terrain = dict() #TODO
    
    def set_pop_move_manager(self, manager):
        self.pop_move_manager = manager
    
    def get_size(self):
        return (self.width, self.height)
    
    def set_height(self, height):
        self.height = height
    
    def set_width(self, width):
        self.width = width
    
    def get_seed(self):
        return self.seed
    
    def set_seed(self, seed):
        self.seed = seed
    
    def set_chunk_size(self, size):
        self.chunk_size = size
        self.chunk_manager.set_chunk_size(size)
    
    def add_pop_at(self, location):
        # Add pop to tile it should be on, only run this function when adding a new pop, not an existing pop
        chunk = self.chunk_manager.get_chunk_at(location)
        tile = chunk.get_tile_manager().get_tile(tuple([coord % self.chunk_size for coord in location]))
        
        pop = PopManager().generate_pop(location=location)
        
        PopManager().add_pop(pop)
        
        tile.add_pop(pop)
        chunk.make_dirty()

    def prepare(self):
        # Placeholder for any setup that needs to be done before the simulation starts
        self.generate_terrain()
        self.generate_temperature()
        
        self.chunk_manager.initialize_chunks()
        
        self.generate_map()
    
    def generate_terrain(self):
        self.terrain = WorldGenerator(seed=self.seed).generate_map((self.height, self.width))

    def generate_temperature(self):
        self.biomes = WorldGenerator(seed=self.seed + 1).generate_map((self.height, self.width))
    
    def get_terrain_obj_at(self, x, y) -> Terrain:
        terrain_value = self.terrain[x * self.width + y]
        
        if terrain_value < TerrainHeight.SHALLOW_COASTAL_WATER:
            return Ocean()
        elif terrain_value >= TerrainHeight.SHALLOW_COASTAL_WATER and terrain_value < TerrainHeight.LAND:
            return ShallowCoastalWater()
        elif terrain_value >= TerrainHeight.LAND and terrain_value < TerrainHeight.HILLS:
            return Plains()
        elif terrain_value >= TerrainHeight.HILLS and terrain_value < TerrainHeight.MOUNTAIN:
            return Hills()
        elif terrain_value >= TerrainHeight.MOUNTAIN and terrain_value < TerrainHeight.MOUNTAIN_PEAK:
            return Mountain()
        elif terrain_value >= TerrainHeight.MOUNTAIN_PEAK:
            return MountainPeak()
        else:
            print("Invalid terrain value: " + str(terrain_value))
            return Unland()
    
    def get_biome_type_at(self, x, y) -> Biome:
        land_height = self.terrain[self.width * x + y]
        temperature = self.biomes[self.width * x + y]
        
        if land_height > TerrainHeight.LAND and temperature < Temperature.COLD:
            return BiomeType.ARCTIC
        elif land_height > TerrainHeight.LAND and temperature > Temperature.COLD and temperature < Temperature.HOT:
            return BiomeType.TEMPERATE
        elif land_height > TerrainHeight.LAND and temperature > Temperature.HOT:
            return BiomeType.TROPICAL
        else:
            return BiomeType.DESERT
    
    def get_biome(self, biome_type: BiomeType):
        if biome_type == BiomeType.ARCTIC:
            return Tundra()
        elif biome_type == BiomeType.TEMPERATE:
            return Plains()
        elif biome_type == BiomeType.TROPICAL:
            return Plains()
        elif biome_type == BiomeType.DESERT:
            return Desert()
        else:
            print("Invalid biome type: " + biome_type)
            return None
    
    def get_harvestables(self):
        # Placeholder for getting harvestable resources
        return self.trees
    
    def generate_trees(self):
        for x in range(self.width):
            for y in range(self.height):
                if self.map[x][y].get_biome().get_name() == 'forest':
                    if random.randint(0, 100) < self.map[x][y].get_biome().get_tree_spawn_chance():
                        self.trees.append(AppleTree())
                elif self.map[x][y].biome == 'desert':
                    # Lower chance of trees, different types
                    if random.randint(0, 100) < self.map[x][y].get_biome().get_tree_spawn_chance():
                        self.trees.append(Cactus())

    def generate_animals(self):
        for x in range(self.width):
            for y in range(self.height):
                if self.map[x][y].biome.supports_animals():
                    # Add animals based on biome
                    self.animals.append(Animal(species='deer', location=(x, y), health=100, food_value=50))
    
    # Generate map 2d array that implements terrain and biome maps and adds trees and animals
    def generate_map(self):
        chunk_manager = self.chunk_manager
        
        for x in range(self.width):
            for y in range(self.height):
                if chunk_manager.has_chunk_at((x, y)) == False:
                    chunk_manager.add_chunk(Chunk(location=(x, y), size=self.chunk_size))
                tile_manager = chunk_manager.get_chunk_at((x, y)).tile_manager
                new_tile = Tile(location=(x, y), local_coordinates=(x % self.chunk_size, y % self.chunk_size), terrain=self.get_terrain_obj_at(x, y), biome=self.get_biome(self.get_biome_type_at(x, y)))
                tile_manager.add_tile(new_tile)
    
    def get_tile(self, location) -> Tile:
        chunk_manager = self.chunk_manager
        chunk = chunk_manager.get_chunk(location)
        tile_manager = chunk.get_tile_manager()
        return tile_manager.get_tile(tuple([coord % chunk.size for coord in location]))
    
    # Find a tile with the given terrain type
    def find_tiles_with_terrain(self, terrain_type) -> Tile:
        chunks = self.chunk_manager.get_chunks()
        found_tiles = []
        
        for chunk in chunks:
            tiles = chunk.get_tile_manager().get_tiles()
            for tile in tiles:
                if tile.terrain == terrain_type:
                    found_tiles.append(tile)
        
        return found_tiles
    
    def update(self):
        # Update the world state for a new simulation step
        
        # Trigger updates for all pops in the world
        PopManager().update()

        # Optionally, update resources, weather, or other global factors
        pass
    
    def render(self, surface, filename=None, scale=1, output=RenderOutput.FILE, screen=None):
        
        tile_renderer = TileRenderer(None)
        
        chunks = self.chunk_manager.get_chunks()
        chunks = self.chunk_manager.get_chunks_to_render()
        
        for chunk in chunks:
            tiles = chunk.get_tile_manager().get_tiles_to_render()
            for tile in tiles:
                tile_renderer.set_tile(tile)
                
                coordinate_colour = tile_renderer.render()
                
                x = (chunk.get_location() + tile.get_location()[0]) * scale
                y = (chunk.get_location() + tile.get_location()[1]) * scale
                coordinate = (x, y)
                size = (scale, scale)
                rect = (coordinate, size)
                
                c = pygame.color.Color(coordinate_colour)
                
                pygame.draw.rect(surface=surface, color=c, rect=rect)
                
                tile.mark_rendered()
            chunk.mark_rendered()
        
        if output == RenderOutput.FILE:
            if filename is None:
                filename = self.seed + ".png"
            
            pygame.image.save(surface=surface, filename=filename)
            return
        elif output == RenderOutput.VARIABLE:
            return surface