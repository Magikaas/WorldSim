import numpy as np

def save_heightmap_compressed(heightmap, filename="heightmap"):
    np.savez_compressed(f"{filename}.npz", heightmap=heightmap)

def load_heightmap_compressed(filename="heightmap"):
    data = np.load(f"{filename}.npz")
    return data['heightmap']
