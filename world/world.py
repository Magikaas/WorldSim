from __future__ import annotations
from typing import List

import random
import pygame

from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder, DiagonalMovement
from sympy import O

from object_types import Location
from world.terrain import Terrain, TerrainHeight
from world.biome import Temperature, BiomeType
from world.terrain import *

from world.chunkmanager import ChunkManager
from managers.pop_move_manager import PopMoveManager
from managers.pop_move_manager import pop_move_manager as PopMoveManagerInstance
from managers.pop_manager import pop_manager as PopManager

from obj.item import Item

from obj.worldobj.resourcenode import NoResource, ResourceNode

from .generator import MapGenerator
from .tile import Tile
from .chunk import Chunk

from utils.tilerenderer import TileRenderer
from utils.renderoutput import RenderOutput
from utils.rendertype import MapRenderType

from path.path import Path
from path.popmove import PopMove

from utils.logger import Logger

from managers.logger_manager import logger_manager

from observer import RenderableObserver

# Longterm TODO: Make singleton possible with multiple 'Worlds'
class World(RenderableObserver):
    width: int
    height: int
    seed: int
    pop_move_manager: PopMoveManager
    terrain: List[float]
    temperature: List[float] = []
    biomes: List[float] = []
    font: pygame.Font
    
    def __init__(self):
        if hasattr(self, "terrain"): raise ValueError("Somehow got initialized twice")
        self.chunk_manager = ChunkManager(world=self)
        self.pathfinder = AStarFinder(diagonal_movement=DiagonalMovement.always)
        self.pathfinder_prepped = False
        self.render_mode = None
        
        self.logger = Logger("world", logger_manager)
        
        self.paths = {}
    
    def get_size(self):
        return (self.width, self.height)
    
    def set_chunk_size(self, size):
        self.chunk_size = size
        self.chunk_manager.chunk_size = size
    
    def add_pop_at(self, location):
        # Add pop to tile it should be on, only run this function when adding a new pop, not an existing pop
        chunk = self.chunk_manager.get_chunk_at(location)
        tile = chunk.tile_manager.get_tile(tuple([coord % self.chunk_size for coord in location]))
        
        pop = PopManager.generate_pop(location=location, world=self)
        
        PopManager.add_pop(pop)
        
        tile.add_pop(pop)
        chunk.dirty = True

    def prepare(self):
        # Placeholder for any setup that needs to be done before the simulation starts
        self.logger.debug("Preparing world")
        self.logger.debug("Generating terrain map")
        self.generate_terrain()
        self.logger.debug("Generating temperature map")
        self.generate_temperature()
        
        self.logger.debug("Initializing chunk manager")
        self.chunk_manager.initialize_chunks()
        
        self.logger.debug("Generating map")
        self.generate_map()
        self.logger.debug("Generating resource nodes")
        self.generate_resourcenodes()
    
    def generate_terrain(self):
        self.terrain = MapGenerator(seed=self.seed).generate_map((self.height, self.width), chunk_size=self.chunk_size, octaves=5, name="terrain")

    def generate_temperature(self):
        self.biomes = MapGenerator(seed=self.seed + 1).generate_map((self.height, self.width), chunk_size=self.chunk_size)
    
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
    
    def get_biome_type_at(self, x, y) -> BiomeType:
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
        return None
    
    def generate_resourcenodes(self):
        chunks = self.chunk_manager.chunks
        
        resource_density_map = MapGenerator(seed=self.seed + 2).generate_map((len(chunks), len(chunks[0])), chunk_size=1, octaves=5, name="resource_density")
        # resource_type_map = MapGenerator(seed=self.seed + 3).generate_map((len(chunks), len(chunks[0])), octaves=4, name="resource_type")
        
        max_resource_per_chunk = 5 # TODO: Make this variable
        resources_amount_to_add = 0
        
        max_attempts = 100
        
        resources_added = {}
        
        # Create resource nodes
        for chunk_row in chunks:
            for chunk in chunk_row:
                # Chunk's location in world
                chunk_x = int(chunk.location[0] / self.chunk_size)
                chunk_y = int(chunk.location[1] / self.chunk_size)
                
                resource_map_coordinate = chunk_x * int(self.height / self.chunk_size) + chunk_y
                # Density of chunk
                density = (resource_density_map[resource_map_coordinate] + 1) / 2
                
                # If the chunk has enough resource density, add resources
                # TODO: Make this variable
                # TODO: Make this a function of the biome
                if density > 0.15:
                    # Resource count is determined by the density of the chunk, scale 0 to 2 to get 0 to max_resource_per_chunk
                    resources_amount_to_add = max_resource_per_chunk * density * 4
                    
                    failed_adding = 0
                    
                    tile_manager = chunk.tile_manager
                    
                    attempts = 0
                    
                    # Add resources to the chunk
                    while int(resources_amount_to_add) > 0:
                        attempts += 1
                        
                        if attempts > max_attempts:
                            self.logger.debug("Failed adding resources after %s attempts" % str(attempts))
                            break
                        # Resource type to spawn in chunk, currently arbitrary
                        # resource = Oak() if density > 0 else StoneResource()
                        
                        # Random location in chunk
                        resource_x = random.randint(0, chunk.size - 1)
                        resource_y = random.randint(0, chunk.size - 1)
                        
                        tile = tile_manager.get_tile((resource_x, resource_y))
                        
                        if type(tile.resourcenode) is not type(NoResource()):
                            # If the tile already has a resource node, skip this tile
                            continue
                        
                        if len(tile.terrain.possible_resources) == 0:
                            # If the terrain does not have any possible resources, skip this tile
                            resources_amount_to_add = 0
                            continue
                        
                        resource = tile.terrain.possible_resources[random.randint(0, len(tile.terrain.possible_resources) - 1)] if density > 0 else None
                        
                        if resource is None:
                            continue
                        
                        added_resource = tile.resourcenode = resource()
                        
                        if resources_added.get(resource().name) is None:
                            resources_added[resource().name] = 1
                        else:
                            resources_added[resource().name] += 1
                        
                        if added_resource:
                            resources_amount_to_add -= 1
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
        
        self.logger.debug("Generating map chunks")
        for x in range(self.width):
            for y in range(self.height):
                chunk = None
                if chunk_manager.has_chunk_at((x, y)) == False:
                    chunk = Chunk(location=(x, y), size=self.chunk_size).initialise()
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
        
        # I'll turn this off for now, as it's not necessary for the current implementation, it also takes a lot of time
        # self.logger.debug("Preparing pathing tiles")
        # self.chunk_manager.prepare_best_pathing_tiles()
    
    def get_tile(self, location) -> Tile:
        chunk_manager = self.chunk_manager
        chunk = chunk_manager.get_chunk(location)
        tile_manager = chunk.tile_manager
        return tile_manager.get_tile(tuple([coord % chunk.size for coord in location]))
    
    def is_land_tile(self, location: Location) -> bool:
        tile = self.get_tile(location)
        
        return tile.terrain != Ocean() and tile.terrain != ShallowCoastalWater()
    
    def get_closest_land_tile_location(self, location: Location) -> Location:
        distance = 1
        x, y = location
        
        while True:
            for i in range(-distance, distance + 1):
                for j in range(-distance, distance + 1):
                    target = (x + i, y + j)
                    if self.is_land_tile(target):
                        return (target[0] % self.width, target[1] % self.height)
            distance += 1
    
    def get_distance_between(self, location1, location2):
        width = self.width
        height = self.height
        
        dx = abs(location1[0] - location2[0])
        dy = abs(location1[1] - location2[1])
        
        wraparound_dx = min(dx, width - dx)
        wraparound_dy = min(dy, height - dy)
        
        return wraparound_dx + wraparound_dy
    
    # Find a tile with the given terrain type
    def find_tiles_with_terrain(self, terrain_type) -> List[Tile]:
        chunks = self.chunk_manager.chunks
        found_tiles = []
        
        for chunk_row in chunks:
            for chunk in chunk_row:
                tiles = chunk.tile_manager.tiles
                for tile_row in tiles:
                    for tile in tile_row:
                        if tile.terrain == terrain_type:
                            found_tiles.append(tile)
        
        return found_tiles
    
    def trigger_force_render(self):
        self.chunk_manager.make_all_dirty()
    
    def render(self, surface, filename=None, scale=1, output=RenderOutput.FILE, screen=None, map_render_type=MapRenderType.ALL, force_render=False) -> pygame.Surface:
        tile_renderer = TileRenderer()
        
        if force_render:
            chunks = self.chunk_manager.chunks
        else:
            chunks = self.chunk_manager.get_dirty_chunks()
        
        for chunk_list in chunks:
            for chunk in chunk_list:
                if chunk is None:
                    # This chunk has not been generated yet
                    continue
                
                if force_render:
                    tiles = chunk.tile_manager.tiles
                else:
                    tiles = chunk.tile_manager.get_dirty_tiles()
                for tiles_row in tiles:
                    for tile in tiles_row:
                        tile_renderer.tile = tile
                        coordinate_colour = tile_renderer.render(map_render_type=map_render_type)
                        
                        pixel_x = (chunk.location[0] + tile.local_coordinates[0]) * scale
                        pixel_y = (chunk.location[1] + tile.local_coordinates[1]) * scale
                        coordinate = (pixel_x, pixel_y)
                        size = (scale, scale)
                        rect = (coordinate, size)
                        
                        c = pygame.color.Color(coordinate_colour)
                        
                        pygame.draw.rect(surface=surface, color=c, rect=rect)
                        
                        resource_node = tile.resourcenode
                        
                        if resource_node is not None and type(resource_node) is not type(NoResource()):
                            font = pygame.font.SysFont('robotoregular', 8)
                            resource_text = font.render(resource_node.harvestable_resource.name[0], 1, (255, 255, 255))
                            surface.blit(resource_text, (tile.location[0] * scale, tile.location[1] * scale))
                        
                        tile.dirty = False
                chunk.dirty = False
        
        if output == RenderOutput.FILE:
            if filename is None:
                return surface
            
            pygame.image.save(surface=surface, file=filename)
            return surface
        elif output == RenderOutput.VARIABLE:
            return surface
    
    # Observer notify
    def notify(self, subject):
        subject.dirty = True
    
    def get_all_tiles_within_distance(self, location: Location, distance: int = 5) -> List[Tile]:
        # Find resource nodes near the location
        search_chunks = []
        
        # Fetch all chunks within the distance
        for x in range(-distance // self.chunk_size, distance // self.chunk_size + 1):
            for y in range(-distance // self.chunk_size, distance // self.chunk_size + 1):
                chunk = self.chunk_manager.get_chunk_at(((location[0] + x * self.chunk_size) % self.width, (location[1] + y * self.chunk_size) % self.height))
                if chunk not in search_chunks:
                    search_chunks.append(chunk)
        
        return search_chunks
    
    def find_closest_location(self, start: Location, location_list: List[tuple], entity, max_distance: int = 0) -> tuple:
        if max_distance == 0:
            max_distance = self.width
        
        closest_location = None
        closest_distance = self.width
        
        use_pathfinding = False
        
        for location in location_list:
            if self.get_distance_between(start, location) > max_distance:
                # self.logger.warn("Location", location, "is too far away from", start, actor=entity)
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
    
    def find_tiles_with_resourcenodes_near(self, location: Location, resourcenode_type: ResourceNode, distance: int = 5) -> List[Tile]:
        search_chunks = self.get_all_tiles_within_distance(location=location, distance=distance)
        
        resourcenode_tiles = []
        
        for chunk in search_chunks:
            tiles = chunk.tile_manager.tiles
            for tiles_row in tiles:
                for tile in tiles_row:
                    # If the tile is within the distance, add its resource nodes to the list
                    if abs(tile.location[0] - location[0]) <= distance and abs(tile.location[1] - location[1]) <= distance:
                        resourcenode = tile.resourcenode
                        
                        if isinstance(resourcenode, resourcenode_type):
                            resourcenode_tiles.append(tile)
        
        return resourcenode_tiles
    
    def find_tiles_with_resource_near(self, location: Location, resource_type: type, distance: int = 5) -> List[Tile]:
        search_chunks = self.get_all_tiles_within_distance(location=location, distance=distance)
        
        resourcenode_tiles = []
        
        for chunk in search_chunks:
            tiles = chunk.tile_manager.tiles
            for tiles_row in tiles:
                for tile in tiles_row:
                    # If the tile is within the distance, add its resource nodes to the list
                    if abs(tile.location[0] - location[0]) <= distance and abs(tile.location[1] - location[1]) <= distance:
                        if tile.resourcenode is not None:
                            if isinstance(resource_type, Item):
                                if isinstance(tile.resourcenode.harvestable_resource, type(resource_type)):
                                    resourcenode_tiles.append(tile)
                            else:
                                # If the resource type is not an item, check if the resource node is a type of item
                                if isinstance(tile.resourcenode.harvestable_resource, resource_type):
                                    resourcenode_tiles.append(tile)
        
        return resourcenode_tiles
    
    def pathfind_pop(self, pop, target_location: Location):
        # Generate the chunk grid if it's not already generated
        chunkgrid = self.get_chunk_based_pathing_grid()
        
        # Create a grid object for the pathfinder
        chunkgrid_nodes = Grid(width=len(chunkgrid[0]), height=len(chunkgrid), matrix=chunkgrid, grid_id=1)
        
        # Find a path between the pop's location and the target location
        chunk_nodepath = self.pathfind(pop, target_location, grid=chunkgrid_nodes)
        
        path = Path(pop)
    
    def pathfind(self, pop, target_location: Location, grid=None):
        if grid is None:
            grid, offsets = self.prep_pathfinder(pop.location, target_location)
        
        nodepath = None
        
        while nodepath is None:
            try:
                start_node = ((pop.location[0] - offsets[0]) % self.width, (pop.location[1] - offsets[1]) % self.width)
                end_node = ((target_location[0] - offsets[0]) % self.height, (target_location[1] - offsets[1]) % self.height)
                nodepath, runs = self.pathfinder.find_path(start=grid.node((pop.location[0] - offsets[0]) % self.width, (pop.location[1] - offsets[1]) % self.width), end=grid.node((target_location[0] - offsets[0]) % self.height, (target_location[1] - offsets[1]) % self.height), graph=grid)
            except Exception as e:
                self.logger.debug("Error finding path:", e, actor=pop)
        
        self.logger.debug("Created path from", pop.location, "to tile:", target_location, "with length:", len(nodepath), actor=pop)
        
        path = Path(pop)
        
        for node in nodepath:
            x = node.x + offsets[0]
            y = node.y + offsets[1]
            
            move = PopMove(pop, self.get_tile((x, y)))
            path.add_move(move)
        
        return path
    
    def prep_pathfinder(self, start_location: Location, target_location: Location):
        # Padding to make sure the pathfinder can find a path to the target
        padding = 4
        
        # The grid is created based off the start and target location compared to the actual 0,0 location, determine the offset between the two
        # The offset is based on the location closest to the 0,0 location
        
        # If the difference is larger than self.width / 2 or self.height / 2, the offset is the location farthest from the 0,0 location (- padding)
        # because we are wrapping around the world
        if abs(start_location[0] - target_location[0]) > self.width / 2:
            # Wrapping around, so pick the location farthest from the 0,0 location
            offset_x = max(start_location[0], target_location[0]) - padding
            grid_width = padding*2 + self.width - abs(start_location[0] - target_location[0])
        else:
            # No wrapping, pick the closest location to the 0,0 location
            offset_x = min(start_location[0], target_location[0]) - padding
            grid_width = padding*2 + abs(start_location[0] - target_location[0])
        
        if abs(start_location[1] - target_location[1]) > self.height / 2:
            # Wrapping around, so pick the location farthest from the 0,0 location
            offset_y = max(start_location[1], target_location[1]) - padding
            grid_height = padding*2 + self.height - abs(start_location[1] - target_location[1])
        else:
            # No wrapping, pick the closest location to the 0,0 location
            offset_y = min(start_location[1], target_location[1]) - padding
            grid_height = padding*2 + abs(start_location[1] - target_location[1])
        
        offsets = (offset_x % self.width, offset_y % self.height)
        
        # Make 2 dimensional array with all the tiles in the world
        gridnodes = [[1 for j in range(grid_width)] for i in range(grid_height)]
        
        # Cache tiles for each chunk that is within the area of the pathfinder grid
        chunk_tiles = {}
        
        # Make the tiles around the target location passable and adjust the value based on the tile's speed multiplier
        for x in range(grid_height):
            for y in range(grid_width):
                # Determine the true x and y coordinates of the tile
                true_x = (start_location[0] + x) % self.width
                true_y = (start_location[1] + y) % self.height
                
                if chunk_tiles.get((true_x // self.chunk_size, true_y // self.chunk_size)) is None:
                    chunk = self.chunk_manager.get_chunk_at((true_x, true_y))
                    chunk_tiles[(true_x // self.chunk_size, true_y // self.chunk_size)] = chunk.tile_manager.tiles
                
                # Determine the true x and y coordinates of the chunk within the chunk grid
                chunk_true_x = true_x // self.chunk_size
                chunk_true_y = true_y // self.chunk_size
                
                # Determine the true x and y coordinates of the tile within the chunk
                chunk_x = true_x % self.chunk_size
                chunk_y = true_y % self.chunk_size
                
                tile = chunk_tiles[(chunk_true_x, chunk_true_y)][chunk_x][chunk_y]
                
                if tile.terrain is Ocean() or tile.terrain is ShallowCoastalWater():
                    weight = 1000
                else:
                    weight = (1 / tile.terrain.speed_multiplier if tile.terrain.speed_multiplier > 0 else 0)
                
                gridnodes[x][y] = weight
        
        grid = Grid(width=len(gridnodes), height=len(gridnodes[0]), matrix=gridnodes, grid_id=0)
        
        self.pathfinder_prepped = True
        
        return grid, offsets
    
    def get_chunk_based_pathing_grid(self):
        chunks = self.chunk_manager.chunks
        
        grid = []
        
        for chunk_row in chunks:
            grid_row = []
            for chunk in chunk_row:
                average_cost = chunk.get_average_pathing_cost()
                
                # If the pathing cost is too high, make the chunk impassable, to ease up on the pathfinding calculations
                grid_row.append(average_cost)
                # grid_row.append(1 if average_cost < 4 else 0)
            grid.append(grid_row)
        
        return grid
    
    def update(self):
        PopManager.update()
        
        PopMoveManagerInstance.handle_moves()

world = World()