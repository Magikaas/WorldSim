from __future__ import annotations

from world.chunk import Chunk

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    import world

class ChunkManager:
    def __init__(self, world: world.World):
        self.world = world
        self.chunks = []
        self.chunk_size = 0
    
    def initialize_chunks(self):
        self.chunks = [[0] * int(self.world.height / self.chunk_size) for i in range(int(self.world.width / self.chunk_size))]
    
    def add_chunk(self, chunk: Chunk):
        chunk_x = int(chunk.get_location()[0] / self.chunk_size)
        chunk_y = int(chunk.get_location()[1] / self.chunk_size)
        if len(self.chunks) < chunk_x or len(self.chunks[0]) < chunk_y:
            print("Chunk location out of bounds: %s" % chunk.get_location() / self.chunk_size)
            return
        
        self.chunks[chunk_x][chunk_y] = chunk
    
    def set_chunk_size(self, size):
        self.chunk_size = size
    
    def get_chunk_size(self):
        return self.chunk_size
    
    def has_chunk_at(self, location) -> bool:
        return isinstance(self.chunks[int((location[0] - (location[0] % self.chunk_size)) / self.chunk_size)][int((location[1] - (location[1] % self.chunk_size)) / self.chunk_size)], Chunk)
    
    def remove_chunk(self, chunk: Chunk):
        self.chunks.remove(chunk)
    
    def get_chunks(self) -> List[Chunk]:
        return self.chunks
    
    def get_chunk_at(self, location) -> Chunk:
        return self.chunks[int((location[0] - (location[0] % self.chunk_size)) / self.chunk_size)][int((location[1] - (location[1] % self.chunk_size)) / self.chunk_size)]
    
    def get_chunks_to_render(self) -> List[Chunk]:
        chunks = []
        for chunk_row in self.chunks:
            for chunk in chunk_row:
                if chunk.dirty:
                    chunks.append(chunk)
                # else:
                #     print("Skipped chunk ", chunk.get_location())
        return chunks
    
    def get_chunk(self, location) -> Chunk:
        chunk_x = int(location[0] / self.chunk_size) % len(self.chunks)
        chunk_y = int(location[1] / self.chunk_size) % len(self.chunks[chunk_x])
        return self.chunks[chunk_x][chunk_y]