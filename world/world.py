from __future__ import annotations
from typing import List

import random
import pygame
import copy

from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder, DiagonalMovement

from world.terrain import Terrain, TerrainHeight
from world.biome import Biome, Temperature, BiomeType
from world.terrain import *

from world.chunkmanager import ChunkManager
from managers.pop_move_manager import PopMoveManager
from managers.pop_manager import PopManager

from obj.item import Item

from obj.worldobj.resourcenode import ResourceNode, Oak, StoneResource

from .generator import MapGenerator
from .tile import Tile
from .chunk import Chunk

from utils.tilerenderer import TileRenderer
from utils.renderoutput import RenderOutput
from utils.rendertype import MapRenderType

from path.path import Path
from path.popmove import PopMove

from utils.logger import Logger

from observer import RenderableObserver

# Longterm TODO: Make singleton possible with multiple 'Worlds'
class World(RenderableObserver):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(World, cls).__new__(cls)
            
            cls._instance.__init__(**kwargs)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            
            self.terrain = None
            self.temperature = None
            self.biomes = None
            self.chunk_manager = ChunkManager(world=self)
            self.pathfinder = AStarFinder(diagonal_movement=DiagonalMovement.never)
            self.grid = None
            self.pathfinder_prepped = False
            self.render_mode = None
            
            self.logger = Logger("world")
    
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
            self.logger.debug("Invalid terrain value: " + str(terrain_value))
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
            self.logger.debug("Invalid biome type: " + biome_type)
            return None
    
    def get_harvestables(self):
        # Placeholder for getting harvestable resources
        return self.trees
    
    def generate_resourcenodes(self):
        chunks = self.chunk_manager.get_chunks()
        
        resource_density_map = MapGenerator(seed=self.seed + 2).generate_map((len(chunks), len(chunks[0])), octaves=5, name="resource_density")
        resource_type_map = MapGenerator(seed=self.seed + 3).generate_map((len(chunks), len(chunks[0])), octaves=4, name="resource_type")
        
        max_resource_per_chunk = 5 # TODO: Make this variable
        resources_to_add = 0
        
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
                    resources_to_add = max_resource_per_chunk * (density + 1 / 2)
                    
                    failed_adding = 0
                    
                    tile_manager = chunk.get_tile_manager()
                    
                    # Add resources to the chunk
                    while int(resources_to_add) > 0:
                        # Resource type to spawn in chunk, currently arbitrary
                        resource = Oak() if resource_type_map[resource_map_coordinate] > 0 else StoneResource()
                        
                        # Random location in chunk
                        resource_x = random.randint(0, chunk.size - 1)
                        resource_y = random.randint(0, chunk.size - 1)
                        
                        added_resource = tile_manager.get_tile((resource_x, resource_y)).add_resourcenode(resource)
                        
                        if added_resource:
                            resources_to_add -= 1
                        else:
                            # If the resource node could not be added, try again
                            failed_adding += 1
                            continue
        
        self.logger.debug("Failed adding resources:", failed_adding)

    def generate_animals(self):
        # TODO
        pass
    
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
    
    def set_font(self, font):
        self.font = font
    
    def render(self, surface, filename=None, scale=1, output=RenderOutput.FILE, screen=None, map_render_type=MapRenderType.ALL):
        tile_renderer = TileRenderer(None)
        
        chunks = self.chunk_manager.get_dirty_chunks()
        
        for chunk_list in chunks:
            for chunk in chunk_list:
                tiles = chunk.get_tile_manager().get_dirty_tiles()
                for tiles_row in tiles:
                    for tile in tiles_row:
                        if self.render_mode is not None and self.render_mode == MapRenderType.PATHFINDING:
                            location = tile.location
                            
                            node = self.used_grid.nodes[location[0]][location[1]]
                            
                            tile.dirty = True
                            
                            coordinate_colour = (0, 0, 0 if node.g == 0 else 255 / node.g)
                        else:
                            tile_renderer.set_tile(tile)
                            
                            coordinate_colour = tile_renderer.render(map_render_type=map_render_type)
                        
                        x = (chunk.get_location()[0] + tile.get_local_coordinates()[0]) * scale
                        y = (chunk.get_location()[1] + tile.get_local_coordinates()[1]) * scale
                        coordinate = (x, y)
                        size = (scale, scale)
                        rect = (coordinate, size)
                        
                        c = pygame.color.Color(coordinate_colour)
                        
                        pygame.draw.rect(surface=surface, color=c, rect=rect)
                        
                        resource_node = tile.get_resourcenode()
                        
                        if resource_node is not None:
                            resource_text = self.font.render(resource_node.get_resource_type().name, 1, (255, 255, 255))
                            surface.blit(resource_text, (tile.location[0] * scale, tile.location[1] * scale))
                        
                        # text_x = coordinate[0]
                        # text_y = coordinate[1]
                        # text = self.font.render(str(int(x/scale)) + "," + str(int(y/scale)), 1, (255, 255, 255))
                        # surface.blit(text, (text_x, text_y))
                        
                        tile.mark_rendered()
                chunk.mark_rendered()
        
        # pops = PopManager().get_pops()
        
        # for pop in pops:
        #     location = pop.location
        #     x = location[0] * scale
        #     y = location[1] * scale
        #     text = self.font.render(pop.name, 1, (255, 255, 255))
        #     surface.blit(text, (x, y))
        
        if output == RenderOutput.FILE:
            if filename is None:
                return surface
            
            pygame.image.save(surface=surface, file=filename)
            return surface
        elif output == RenderOutput.VARIABLE:
            return surface
    
    # Observer notify
    def notify(self, subject):
        subject.make_dirty()
    
    def get_all_tiles_within_distance(self, location: tuple, distance: int = 5) -> List[Tile]:
        # Find resource nodes near the location
        search_chunks = []
        
        multipliers = [-1, 1]
        
        # Fetch all chunks within the distance
        for horizontal in multipliers:
            for vertical in multipliers:
                location_horizontal = location[0] + horizontal * distance
                location_vertical = location[1] + vertical * distance
                
                while location_horizontal < 0:
                    location_horizontal = self.width + location_horizontal
                while location_horizontal >= self.width:
                    location_horizontal = location_horizontal - self.width
                
                while location_vertical < 0:
                    location_vertical = self.height + location_vertical
                while location_vertical >= self.height:
                    location_vertical = location_vertical - self.height
                
                corner_location = (location_horizontal, location_vertical)
                
                chunk = self.chunk_manager.get_chunk_at(corner_location)
                
                if chunk not in search_chunks:
                    search_chunks.append(chunk)
        
        return search_chunks
    
    def find_closest_location(self, start: tuple, location_list: List[tuple], entity, max_distance: int = 25) -> tuple:
        closest_location = None
        closest_distance = 1000
        
        use_pathfinding = True
        
        for location in location_list:
            if self.get_distance_between(start, location) > max_distance:
                continue
            
            if use_pathfinding:
                path = self.pathfind(entity, location)
                distance = len(path.moves)
            else:
                distance = self.get_distance_between(start, location)
            
            if closest_location is None or distance < closest_distance:
                closest_location = location
                closest_distance = distance
        
        return closest_location
    
    def find_tiles_with_resourcenodes_near(self, location: tuple, resourcenode_type: ResourceNode, distance: int = 5) -> List[Tile]:
        search_chunks = self.get_all_tiles_within_distance(location=location, distance=distance)
        
        resourcenode_tiles = []
        
        for chunk in search_chunks:
            tiles = chunk.get_tile_manager().get_tiles()
            for tiles_row in tiles:
                for tile in tiles_row:
                    # If the tile is within the distance, add its resource nodes to the list
                    if abs(tile.location[0] - location[0]) <= distance and abs(tile.location[1] - location[1]) <= distance:
                        resourcenode = tile.get_resourcenode()
                        
                        if isinstance(resourcenode, resourcenode_type):
                            resourcenode_tiles.append(tile)
        
        return resourcenode_tiles
    
    def find_tiles_with_resource_near(self, location: tuple, resource_type: Item, distance: int = 5) -> List[Tile]:
        search_chunks = self.get_all_tiles_within_distance(location=location, distance=distance)
        
        resourcenode_tiles = []
        
        for chunk in search_chunks:
            tiles = chunk.get_tile_manager().get_tiles()
            for tiles_row in tiles:
                for tile in tiles_row:
                    # If the tile is within the distance, add its resource nodes to the list
                    if abs(tile.location[0] - location[0]) <= distance and abs(tile.location[1] - location[1]) <= distance:
                        if tile.get_resourcenode() is not None:
                            if isinstance(resource_type, Item):
                                if isinstance(tile.get_resourcenode().get_resource_type(), type(resource_type)):
                                    resourcenode_tiles.append(tile)
                            else:
                                # If the resource type is not an item, check if the resource node is a type of item
                                if isinstance(tile.get_resourcenode().get_resource_type(), resource_type):
                                    resourcenode_tiles.append(tile)
        
        return resourcenode_tiles
    
    def pathfind(self, pop, target_location: tuple):
        self.prep_pathfinder()
        
        grid = copy.copy(self.grid)
        
        nodepath = None
        
        while nodepath is None:
            try:
                nodepath, runs = self.pathfinder.find_path(start=grid.node(pop.location[0], pop.location[1]), end=grid.node(target_location[0], target_location[1]), graph=grid)
            except Exception as e:
                self.logger.debug("Error finding path:", e)
        
        if len(nodepath) == 0:
            self.used_grid = grid
            # self.render_mode = MapRenderType.PATHFINDING
        
        path = Path(pop)
        
        self.logger.debug("Created path for pop:", pop.id, pop.location, "to tile:", target_location, "with length:", len(nodepath))
        
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
        PopManager().update()
        
        PopMoveManager().handle_moves()
        
        pops = PopManager().get_idle_pops()