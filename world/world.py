from __future__ import annotations

import random
import pygame

from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder, DiagonalMovement

from world.terrain import Terrain, TerrainHeight
from world.biome import Biome, Temperature, BiomeType
from world.terraintype import *

from helpers.chunkmanager import ChunkManager
from helpers.popmovemanager import PopMoveManager
from helpers.popmanager import PopManager

from obj.worldobj.appletree import AppleTree
from obj.worldobj.cactus import Cactus
from obj.worldobj import Animal

from obj.worldobj.worldobjecttype.resourcenode import ResourceNode

from .generator import MapGenerator
from .tile import Tile
from .chunk import Chunk

from render.tilerenderer import TileRenderer
from render.renderoutput import RenderOutput
from render.rendertype import MapRenderType

from path.path import Path
from path.popmove import PopMove

from observers import RenderableObserver

# Longterm TODO: Make singleton possible with multiple 'Worlds'
class World(RenderableObserver):
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
            self.pathfinder = AStarFinder(diagonal_movement=DiagonalMovement.never)
            self.grid = None
            self.pathfinder_prepped = False
    
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
        
        pop = PopManager().generate_pop(location=location, world=self)
        
        PopManager().add_pop(pop)
        
        tile.add_pop(pop)
        chunk.make_dirty()

    def prepare(self):
        # Placeholder for any setup that needs to be done before the simulation starts
        self.generate_terrain()
        self.generate_temperature()
        
        self.chunk_manager.initialize_chunks()
        
        self.generate_map()
        self.generate_resourcenodes()
    
    def generate_terrain(self):
        self.terrain = MapGenerator(seed=self.seed).generate_map((self.height, self.width), octaves=5, name="terrain")

    def generate_temperature(self):
        self.biomes = MapGenerator(seed=self.seed + 1).generate_map((self.height, self.width))
    
    def get_terrain_obj_at(self, x, y) -> Terrain:
        terrain_value = self.terrain[y * self.width + x]
        
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
        land_height = self.terrain[y * self.width + x]
        temperature = self.biomes[y * self.width + x]
        
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
    
    def generate_resourcenodes(self):
        chunks = self.chunk_manager.get_chunks()
        
        resource_density_map = MapGenerator(seed=self.seed + 2).generate_map((len(chunks), len(chunks[0])), octaves=5, name="resource_density")
        resource_type_map = MapGenerator(seed=self.seed + 3).generate_map((len(chunks), len(chunks[0])), octaves=4, name="resource_type")
        
        max_resource_per_chunk = 5 # TODO: Make this variable
        resource_count = 0
        
        # Create resource nodes
        for chunk_row in chunks:
            for chunk in chunk_row:
                # Chunk's location in world
                chunk_x = int(chunk.get_location()[0] / self.chunk_size)
                chunk_y = int(chunk.get_location()[1] / self.chunk_size)
                
                resource_map_coordinate = chunk_x * int(self.height / self.chunk_size) + chunk_y
                # Density of chunk
                density = resource_density_map[resource_map_coordinate]
                
                # If the chunk has enough resource density, add resources
                # TODO: Make this variable
                # TODO: Make this a function of the biome
                if density > -0.3:
                    # Resource count is determined by the density of the chunk, scale 0 to 2 to get 0 to max_resource_per_chunk
                    resource_count = max_resource_per_chunk * (density + 1 / 2)
                    
                    # Add resources to the chunk
                    for i in range(int(resource_count)):
                        # Resource type to spawn in chunk, currently arbitrary
                        resource = AppleTree() if resource_type_map[resource_map_coordinate] > 0 else Cactus()
                        
                        # Random location in chunk
                        resource_x = random.randint(0, chunk.size - 1)
                        resource_y = random.randint(0, chunk.size - 1)
                        
                        chunk.get_tile_manager().get_tile((resource_x, resource_y)).add_resourcenode(resource)

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
                chunk = None
                if chunk_manager.has_chunk_at((x, y)) == False:
                    chunk = Chunk(location=(x, y), size=self.chunk_size)
                    chunk.register_observer(self)
                    chunk_manager.add_chunk(chunk)
                else:
                    chunk = chunk_manager.get_chunk_at((x, y))
                tile_manager = chunk.tile_manager
                new_tile = Tile(
                    location=(x, y),
                    local_coordinates=(x % self.chunk_size, y % self.chunk_size),
                    terrain=self.get_terrain_obj_at(x, y),
                    biome=self.get_biome(self.get_biome_type_at(x, y))
                )
                new_tile.register_observer(chunk)
                tile_manager.add_tile(new_tile)
    
    def get_tile(self, location) -> Tile:
        chunk_manager = self.chunk_manager
        chunk = chunk_manager.get_chunk(location)
        tile_manager = chunk.get_tile_manager()
        return tile_manager.get_tile(tuple([coord % chunk.size for coord in location]))
    
    def get_distance_between(self, location1, location2):
        return abs(location1[0] - location2[0]) + abs(location1[1] - location2[1])
    
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
    
    def render(self, surface, filename=None, scale=1, output=RenderOutput.FILE, screen=None, map_render_type=MapRenderType.ALL):
        
        tile_renderer = TileRenderer(None)
        
        chunks = self.chunk_manager.get_chunks()
        chunks = self.chunk_manager.get_chunks_to_render()
        
        for chunk in chunks:
            tiles = chunk.get_tile_manager().get_tiles_to_render()
            for tile in tiles:
                tile_renderer.set_tile(tile)
                
                coordinate_colour = tile_renderer.render(map_render_type=map_render_type)
                
                x = (chunk.get_location()[0] + tile.get_local_coordinates()[0]) * scale
                y = (chunk.get_location()[1] + tile.get_local_coordinates()[1]) * scale
                coordinate = (x, y)
                size = (scale, scale)
                rect = (coordinate, size)
                
                c = pygame.color.Color(coordinate_colour)
                
                pygame.draw.rect(surface=surface, color=c, rect=rect)
                
                tile.mark_rendered()
            chunk.mark_rendered()
        
        if output == RenderOutput.FILE:
            if filename is None:
                filename = str(self.seed) + ".png"
            
            pygame.image.save(surface=surface, file=filename)
            return surface
        elif output == RenderOutput.VARIABLE:
            return surface
    
    # Observer notify
    def notify(self, subject):
        subject.make_dirty()
    
    def find_tiles_with_resourcenodes_near(self, location: tuple, resourcenode_type: ResourceNode, distance: int = 5) -> List[Tile]:
        # Find resource nodes near the location
        search_chunks = []
        
        multipliers = [-1, 1]
        
        for horizontal in multipliers:
            for vertical in multipliers:
                location_horizontal = location[0] + horizontal * distance
                location_vertical = location[1] + vertical * distance
                
                if location_horizontal < 0:
                    location_horizontal = self.width + location_horizontal
                elif location_horizontal >= self.width:
                    location_horizontal = location_horizontal - self.width
                
                if location_vertical < 0:
                    location_vertical = self.height + location_vertical
                elif location_vertical >= self.height:
                    location_vertical = location_vertical - self.height
                
                corner_location = (location_horizontal, location_vertical)
                
                chunk = self.chunk_manager.get_chunk_at(corner_location)
                
                if chunk not in search_chunks:
                    search_chunks.append(chunk)
        
        resourcenode_tiles = []
        
        for chunk in search_chunks:
            tiles = chunk.get_tile_manager().get_tiles()
            for tiles_row in tiles:
                for tile in tiles_row:
                    # If the tile is within the distance, add its resource nodes to the list
                    if abs(tile.location[0] - location[0]) <= distance and abs(tile.location[1] - location[1]) <= distance:
                        resourcenodes = tile.get_resourcenodes()
                        for resourcenode in resourcenodes:
                            # If the resourcenode is of the type we are looking for, add it to the list
                            if isinstance(resourcenode, resourcenode_type):
                                resourcenode_tiles.append(tile)
        
        return resourcenode_tiles
    
    def pathfind(self, pop, target_location: tuple):
        self.prep_pathfinder()
        # try:
        nodepath, runs = self.pathfinder.find_path(start=self.grid.node(pop.location[0], pop.location[1]), end=self.grid.node(target_location[0], target_location[1]), graph=self.grid)
        # except Exception as e:
        #     print("Error finding path:", e)
        #     return None
        
        path = Path(pop)
        
        print("Created path for pop:", pop.id, "to tile:", target_location, "with length:", len(nodepath))
        
        for node in nodepath:
            x = node.x
            y = node.y
            
            move = PopMove(pop, self.get_tile((x, y)))
            path.add_move(move)
        
        return path
    
    def prep_pathfinder(self):
        chunks = self.chunk_manager.get_chunks()
        
        # Make 2 dimensional array with all the tiles in the world
        gridnodes = [[0 for j in range(self.width)] for i in range(self.height)]
        
        for chunk_row in chunks:
            for chunk in chunk_row:
                tiles = chunk.get_tile_manager().get_tiles()
                
                for tiles_row in tiles:
                    for tile in tiles_row:
                        gridnodes[tile.location[1]][tile.location[0]] = 1 / tile.terrain.speed_multiplier if tile.terrain.speed_multiplier > 0 else 0
        
        self.grid = Grid(width=self.width, height=self.height, matrix=gridnodes, grid_id=0)
        
        self.grid.set_passable_left_right_border()
        self.grid.set_passable_up_down_border()
        
        self.pathfinder_prepped = True
    
    def update(self):
        # Update the world state for a new simulation step
        
        # Trigger updates for all pops in the world
        PopManager().update()
        
        PopMoveManager().handle_moves()
        
        pops = PopManager().get_idle_pops()
        
        # For pathing testing purposes only
        # for pop in pops:
        #     pop_chunk = self.chunk_manager.get_chunk_at((0, 0))
        #     target_tile = pop_chunk.get_tile_manager().get_tile((0, 0))
            
        #     path = self.pathfind(pop, target_tile)
            
        #     pop.set_path(path)
            
        #     PopManager().update_pop(pop)