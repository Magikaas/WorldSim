from worldgen.tile import Tile
from obj.worldobj.worldobjecttype.tree import Tree
from obj.worldobj.worldobjecttype.pop import Pop

class TileRenderer():
    def __init__(self, tile: Tile):
        self.tile = tile
    
    def render(self):
        world_obj = self.get_tile().get_world_obj()
        
        coordinate_colour = None
        
        # Check if the tile has a pop or object in it
        # If so, render the pop or object
        if world_obj is not None:
            if isinstance(world_obj, Pop):
                # Render the pop as a purple square
                coordinate_colour = (255, 0, 255)
            elif isinstance(world_obj, Tree):
                # Render the tree as dark green square
                coordinate_colour = (0, 100, 0)
        
        # Set the pixel color based on the biome
        coordinate_colour = self.get_tile().determine_tile_colour()
        
        return coordinate_colour
    
    def get_tile(self):
        return self.tile
    
    def set_tile(self, tile):
        self.tile = tile
        return self