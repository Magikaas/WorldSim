import numpy as np

from helpers.popmanager import PopManager
from helpers.tilemanager import TileManager

from obj.worldobj import AppleTree, Cactus
from obj.worldobj import Animal

from world import WorldGenerator, Tile
from world.terrain import Terrain, TerrainHeight
from world.biome import Biome, Temperature, BiomeType
from world.terraintype import *

from render.tilerenderer import TileRenderer
from render.renderoutput import RenderOutput

from PIL import Image

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
            self.tile_manager = TileManager(world=self)
    
    def set_pop_move_manager(self, manager):
        self.pop_move_manager = manager
        return self
    
    def get_size(self):
        return (self.width, self.height)
    
    def set_height(self, height):
        self.height = height
        return self
    
    def set_width(self, width):
        self.width = width
        return self
    
    def get_seed(self):
        return self.seed
    
    def set_seed(self, seed):
        self.seed = seed
        return self
    
    def add_pop_at(self, location):
        # Add pop to tile it should be on, only run this function when adding a new pop, not an existing pop
        tile = self.get_tile(location[0], location[1])
        
        pop = PopManager().generate_pop(location=(location[0], location[1]))
        
        PopManager().add_pop(pop)
        
        tile.add_pop(pop)
        
        return self
    
    def prepare(self):
        # Placeholder for any setup that needs to be done before the simulation starts
        self.generate_terrain()
        self.generate_temperature()
        
        self.tile_manager.initialize_tiles()
        
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
        for x in range(self.width):
            for y in range(self.height):
                new_tile = Tile(location=(x, y), terrain=self.get_terrain_obj_at(x, y), biome=self.get_biome(self.get_biome_type_at(x, y)))
                self.tile_manager.add_tile(new_tile)
    
    def get_tile(self, x, y) -> Tile:
        return self.tile_manager.get_tile((x, y))
    
    def set_tile(self, x, y, tile: Tile):
        self.map[x][y] = tile
        return self
    
    # Find a tile with the given terrain type
    def find_tile_with_terrain(self, terrain_type) -> Tile:
        found_tiles = []
        for x in range(self.width):
            for y in range(self.height):
                if self.map[x][y].terrain == terrain_type:
                    found_tiles.append(self.map[x][y])
        
        if len(found_tiles) > 0:
            return found_tiles[np.random.randint(0, len(found_tiles))]
        
        return None

    def update(self):
        # Update the world state for a new simulation step
        for pop in PopManager().get_pops():
            pop.update()

        # Optionally, update resources, weather, or other global factors
    
    def render(self, img=None, filename=None, scale=1, output=RenderOutput.FILE, screen=None):
        if img is None:
            img = Image.new(mode="RGB", size=(self.width * scale, self.height * scale), color="white")
        
        tile_renderer = TileRenderer(None)
        
        for x in range(self.width):
            for y in range(self.height):
                tile = self.get_tile(x, y)
                
                if tile.render_me == False:
                    continue
                
                tile_renderer.set_tile(tile)
                
                coordinate_colour = tile_renderer.render()
                
                if scale != 1:
                    for i in range(scale):
                        for j in range(scale):
                            img.putpixel((x * scale + i, y * scale + j), coordinate_colour)
                else:
                    img.putpixel((x, y), coordinate_colour)
        
        if output == RenderOutput.FILE:
            if filename is None:
                filename = self.seed + ".png"
            img.save(filename, "PNG")
            return
        elif output == RenderOutput.DISPLAY:
            img.show()
            return
        elif output == RenderOutput.VARIABLE:
            return img