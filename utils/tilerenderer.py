from world.tile import Tile

from utils.rendertype import MapRenderType

class TileRenderer():
    def __init__(self, tile: Tile):
        self.tile = tile
    
    def render(self, map_render_type=MapRenderType.ALL):
        tile = self.get_tile()
        
        if tile.has_colour_override():
            return tile.get_colour_override()
        
        num_pops = len(tile.get_pops())
        num_animals = len(tile.get_animals())
        has_resourcenode = tile.get_resourcenode() is not None and len(tile.get_resourcenode()) > 0
        
        coordinate_colour = None
        
        # Determine what to render based off MapRenderType enum
        for tile_render_type in MapRenderType:
            if map_render_type.value & tile_render_type.value:
                if self.should_render(map_render_type, MapRenderType.POPS) and num_pops > 0:
                    # Render the pop as a purple square
                    coordinate_colour = (255, 0, 255)
                    break
                elif self.should_render(map_render_type, MapRenderType.ANIMALS) and num_animals > 0:
                    # Render the animal as a brown square
                    coordinate_colour = (139, 69, 19)
                    break
                elif self.should_render(map_render_type, MapRenderType.RESOURCES) and has_resourcenode > 0:
                    # Render the resource node as a bright pink square
                    coordinate_colour = (255, 105, 180)
                    break
                elif self.should_render(map_render_type, MapRenderType.TERRAIN):
                    coordinate_colour = self.get_terrain_colour()
                    break
                else:
                    coordinate_colour = (0, 0, 0)
                    break
        
        tile.mark_rendered()
        
        return coordinate_colour
    
    def should_render(self, render_options, option) -> bool:
        return render_options & option

    def count_pops(self):
        return len(self.get_tile().get_pops())

    def count_animals(self):
        return len(self.get_tile().get_animals())

    def count_resourcenodes(self):
        return len(self.get_tile().get_resourcenode())
    
    def get_terrain_colour(self) -> tuple:
        # Combine the terrain and biome colours
        return self.get_tile().get_terrain().get_colour()
    
    def get_tile(self) -> Tile:
        return self.tile
    
    def set_tile(self, tile):
        self.tile = tile