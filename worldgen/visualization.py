# worldgen/visualization.py
import matplotlib.pyplot as plt

def visualize_world(world, heightmap, temperature):
    # Example visualization using matplotlib
    fig, axs = plt.subplots(1, 2)
    axs[0].imshow(heightmap, cmap='terrain')
    axs[0].set_title('Heightmap')
    axs[1].imshow(biomes, cmap='viridis')
    axs[1].set_title('Biomes')
    plt.show()
