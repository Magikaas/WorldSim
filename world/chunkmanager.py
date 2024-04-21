from __future__ import annotations

from attr import dataclass

from world.chunk import Chunk

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    import world

@dataclass
class ChunkManager:
    world: world.World
    chunks: List[List[Chunk]] = []
    chunk_size: int = 0
    
    def initialize_chunks(self):
        self.chunks = [
            [Chunk((-1, -1)) for _ in range(self.world.height // self.chunk_size)]
            for _ in range(self.world.width // self.chunk_size)
        ]
    
    def add_chunk(self, chunk: Chunk):
        chunk_x = int(chunk.location[0] / self.chunk_size)
        chunk_y = int(chunk.location[1] / self.chunk_size)
        if len(self.chunks) < chunk_x or len(self.chunks[0]) < chunk_y:
            print("Chunk location out of bounds: %s" % str(chunk.location / self.chunk_size))
            return
        
        self.chunks[chunk_x][chunk_y] = chunk
    
    def has_chunk_at(self, location) -> bool:
        chunk = self.chunks[int((location[0] - (location[0] % self.chunk_size)) / self.chunk_size)][int((location[1] - (location[1] % self.chunk_size)) / self.chunk_size)]
        return isinstance(chunk, Chunk) and chunk.initialised
    
    def remove_chunk(self, chunk: Chunk):
        x, y = chunk.location
        del self.chunks[x][y]
    
    def get_chunk_at(self, location) -> Chunk:
        x, y = location
        # return self.chunks[x][y]
        return self.chunks[x // self.chunk_size][y // self.chunk_size]
    
    def make_all_dirty(self):
        for chunk_row in self.chunks:
            for chunk in chunk_row:
                chunk.dirty = True
    
    def get_dirty_chunks(self) -> List[List[Chunk]]:
        dirty_chunks = []
        for chunk_row in self.chunks:
            dirty_row = []
            for chunk in chunk_row:
                if chunk.dirty:
                    dirty_row.append(chunk)
            dirty_chunks.append(dirty_row)
        return dirty_chunks
    
    def get_chunk(self, location) -> Chunk:
        chunk_x = int(location[0] / self.chunk_size) % len(self.chunks)
        chunk_y = int(location[1] / self.chunk_size) % len(self.chunks[chunk_x])
        return self.chunks[chunk_x][chunk_y]