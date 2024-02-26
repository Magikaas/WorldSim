# examples/generate_world.py
from world import WorldGenerator

def main():
    seed = 42
    size = 256
    generator = WorldGenerator(seed=seed)
    world = generator.generate_map(size=size)
    heightmap = generator.generate_map(size)
    temperature_map = generator.generate_map(size)

if __name__ == "__main__":
    main()
