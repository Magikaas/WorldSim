from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor
from dataclasses import field
import os
import pickle

from dataclasses import dataclass

from world.chunk import Chunk

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    import world

@dataclass
class ChunkManager:
    world: world.World
    chunks: List[List[Chunk]] = field(default_factory=list)
    chunk_size: int = 0
    best_pathing_tiles: dict = field(default_factory=dict)
    
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
    
    def get_file_name(self):
        return "output/chunks_%sx%s_%s.txt" % (self.world.width, self.world.height, self.world.seed)
    
    def prepare_best_pathing_tiles(self):
        filename = self.get_file_name()
        
        if os.path.exists(filename):
            self.best_pathing_tiles = pickle.load(open(filename, "rb"))
            return
        
        with ProcessPoolExecutor(max_workers=64) as executor:
            threads = []
            for chunk_row in self.chunks:
                for chunk in chunk_row:
                    threads.append(executor.submit(self.prepare_best_pathing_tile, chunk))
            
            for thread in threads:
                result = thread.result()
                self.best_pathing_tiles[result.location] = result
        
        filename = self.get_file_name()
        
        with open(filename, "wb") as f:
            pickle.dump(self.best_pathing_tiles, f)
        
        return self.best_pathing_tiles
    
    def prepare_best_pathing_tile(self, chunk: Chunk):
        return chunk.get_best_pathing_tile()