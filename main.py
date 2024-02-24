# Using cProfile
import cProfile
import pstats

# examples/generate_world.py
from obj.world import World
from obj.popmanager import PopManager

from helpers import worldhelper

import os

import numpy as np

from init import initialize_pops

def run_simulation(world: World, max_iterations=1000, render=False, render_frequency=1000):
    step_nr = 0
    
    sim_seed = world.get_seed()
    
    world_helper = worldhelper.WorldHelper(world)
    for iteration in range(max_iterations):
        step_nr += 1
        
        if render and step_nr % render_frequency == 0:
            print ("Simulation cycle %d" % step_nr)
            
            # if a folder does not exist, create it
            filename = "output/" + sim_seed + "/simstep_" + step_nr.__str__() + ".png"
            
            if os.path.exists("output") == False:
                os.mkdir("output")
            
            if os.path.exists("output/" + sim_seed) == False:
                os.mkdir("output/" + sim_seed)
            
            world_helper.set_world(world)
            
            world_helper.render_world(filename=filename)
        
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

def prep_simulation():
    # Example setup and execution of the simulation
    world_width = 250  # Example dimension
    world_height = 250  # Example dimension
    initial_pop_count = 10  # Starting number of population units
    seed = "1234"  # For deterministic world generation
    
    np.random.seed(hash(seed) % 2**32)

    # Initialize the world
    world = World(world_width, world_height, seed=seed)
    
    initial_pops = initialize_pops(world, initial_pop_count)
    
    for pop in initial_pops:
        PopManager().add_pop(pop)

    return world

def main():
    world = prep_simulation()
    
    do_render = False  # Set to True to render each step of the simulation to an image file

    run_simulation(world, max_iterations=10000, render=do_render, render_frequency=250)

    print("Simulation complete")

profile = True # Profile the code using cProfile

if __name__ == "__main__":
    pop_manager1 = PopManager()
    pop_manager2 = PopManager()

    assert pop_manager1 is pop_manager2  # This should be true, as both variables refer to the same instance
        
    if profile:
        profiler = cProfile.Profile()
        profiler.enable()
        main()
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats('cumtime')
        stats.print_stats()
    else:
        main()