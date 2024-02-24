from world.tile import Tile
from obj.worldobj.worldobjecttype.tree import Tree
from obj.worldobj.worldobjecttype.pop import Pop

class TileRenderer():
    def __init__(self, tile: Tile):
        self.tile = tile
    
    def render(self):
        tile = self.get_tile()
        
        pops = tile.get_pops()
        animals = tile.get_animals()
        
        coordinate_colour = None
        
        if len(pops) > 0:
            # Render the pop as a purple square
            coordinate_colour = (255, 0, 255)
        elif len(animals) > 0:
            # Render the animal as a brown square
            coordinate_colour = (139, 69, 19)
        else:
            coordinate_colour = self.get_render_info()
        
        return coordinate_colour
    
    def get_render_info(self) -> tuple:
        """Prepare and return information needed for rendering this tile."""
        # This method can be expanded based on what information the renderer needs
        # Example: Return the most dominant feature of the tile for rendering
        if len(self.get_tile().get_trees()) > 0:
            return (0, 255, 0)
        elif len(self.get_tile().get_animals()) > 0:
            return (165, 42, 42)
        elif len(self.get_tile().get_pops()) > 0:
            return (128, 0, 128)
        
        return self.get_terrain_colour()
    
    def get_terrain_colour(self) -> tuple:
        # Combine the terrain and biome colours
        return self.get_tile().get_terrain().get_colour()
    
    def get_tile(self) -> Tile:
        return self.tile
    
    def set_tile(self, tile):
        self.tile = tile
        return self