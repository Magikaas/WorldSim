# examples/generate_world.py
from world import WorldGenerator, visualize_world

def main():
    seed = 42
    size = 256
    generator = WorldGenerator(seed=seed)
    world = generator.generate_map(size=size)
    heightmap = generator.generate_map(size)
    temperature_map = generator.generate_map(size)
    visualize_world(world, heightmap, temperature_map)

if __name__ == "__main__":
    main()
