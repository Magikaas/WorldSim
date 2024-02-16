# examples/generate_world.py
from worldgen import WorldGenerator, visualize_world
from obj.worldobj.pop import Pop
from obj.world import World

from init import initialize_pops, initialize_world, generate_animals, generate_trees
import random

def run_simulation(world, max_iterations=1000):
    for iteration in range(max_iterations):
        # Update the world state, which includes updating all pops within it
        world.update()

        if check_end_conditions(world):
            print(f"Simulation ended at iteration {iteration}")
            break

        # Example: You could add new pops or change the world based on specific conditions
        # if iteration % 100 == 0:
            # world.add_pop(new_pop)

def check_end_conditions(world):
    return len(world.pops) == 0 or world_reached_goal(world)

def world_reached_goal(world: World):
    # Define the conditions for what it means for the world to have "reached its goal"
    if len(world.pops) > 1000:
        return True
    return False  # Placeholder logic

if __name__ == "__main__":
    # Example setup and execution of the simulation
    world_width = 100  # Example dimension
    world_height = 100  # Example dimension
    initial_pop_count = 10  # Starting number of population units
    seed = "your_seed_here"  # For deterministic world generation

    # Initialize the world
    world = World(world_width, world_height, seed=seed)
    
    initial_pops = initialize_pops(world, initial_pop_count)
    
    for pop in initial_pops:
        world.add_pop(pop)

    # Run the simulation
    run_simulation(world, max_iterations=1000)

