from dataclasses import dataclass
from obj.worldobj.resourcenode import NoResource
from world.tile import Tile

from utils.rendertype import MapRenderType

class TileRenderer():
    tile: Tile
    
    def render(self, map_render_type=MapRenderType.ALL):
        tile = self.tile
        
        if tile.has_colour_override():
            return tile.colour_override
        
        num_pops = len(tile.pops)
        num_animals = len(tile.animals)
        has_resourcenode = hasattr(tile, 'resourcenode') and type(tile.resourcenode) is not type(NoResource())
        
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
                elif self.should_render(map_render_type, MapRenderType.RESOURCES) and has_resourcenode:
                    # Render the resource node as a bright pink square
                    coordinate_colour = (255, 105, 180)
                    break
                elif self.should_render(map_render_type, MapRenderType.TERRAIN):
                    coordinate_colour = self.get_terrain_colour()
                    break
                else:
                    coordinate_colour = (0, 0, 0)
                    break
        
        tile.dirty = False
        
        return coordinate_colour
    
    def should_render(self, render_options, option) -> bool:
        return render_options & option

    def count_pops(self):
        return len(self.tile.pops)

    def count_animals(self):
        return len(self.tile.animals)
    
    def get_terrain_colour(self) -> tuple:
        # Combine the terrain and biome colours
        return self.tile.terrain.colour
    