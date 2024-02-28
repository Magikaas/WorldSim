# Using cProfile
import cProfile
import pstats
import pygame
import random

# examples/generate_world.py
from world.world import World
from helpers.popmanager import PopManager
from helpers.popmovemanager import PopMoveManager

from render.renderoutput import RenderOutput

import os

def run_simulation(world: World, max_iterations=1000, render=False, render_frequency=1000):
    step_nr = 0
    
    sim_seed = world.get_seed()
    
    scale = 1
    
    if render:
        clock = pygame.time.Clock()
        
        width = world.get_size()[0]
        height = world.get_size()[1]
        
        world_size = (width * scale, height * scale)
        
        window = pygame.display.set_mode(world_size)
        
        surface = pygame.Surface(world_size)
    
    for iteration in range(max_iterations):
        if render:
            pygame.event.get()
            # clock.tick(60)
        
        step_nr += 1
        
        if render:
            surface = world.render(surface=surface, scale=scale, output=RenderOutput.VARIABLE)
            
            screen_width = world.width * scale / 2
            screen_height = world.height * scale / 2
            
            window.fill(0)
            window.blit(surface, surface.get_rect(center = (screen_width, screen_height)))
            pygame.display.flip()
            
            if step_nr % render_frequency == 0:
                str_seed = str(sim_seed)
                
                # if a folder does not exist, create it
                filename = "output/" + str_seed + "/" + str(world.width) + "x" + str(world.height) + "_scale_" + str(scale) + "_" + str(step_nr) + ".png"
                
                if os.path.exists("output") == False:
                    os.mkdir("output")
                
                if os.path.exists("output/" + str_seed) == False:
                    os.mkdir("output/" + str_seed)
                
                print("Writing map file to " + filename)
                
                surface = world.render(surface=surface, scale=scale, output=RenderOutput.FILE, filename=filename)
                
        
        if iteration % render_frequency == 0:
            print(f"Iteration {iteration}")
        
        # Update the world state, which includes updating all pops within it
        world.update()

        if check_end_conditions(world) and False:
            print(f"Simulation ended at iteration {iteration}")
            break

        # Example: You could add new pops or change the world based on specific conditions
        # if iteration % 100 == 0:
            # world.add_pop(new_pop)

def check_end_conditions(world):
    return len(PopManager().get_pops()) == 0 or world_reached_goal(world)

def world_reached_goal(world: World):
    # Define the conditions for what it means for the world to have "reached its goal"
    if len(PopManager().get_pops()) > 1000:
        return True
    return False  # Placeholder logic

def prep_simulation():
    world_width = 512
    world_height = 256
    initial_pop_count = 10
    seed = 1234
    chunk_size = 16
    
    # np.random.seed(hash(seed) % 2**32)
    
    pop_move_manager = PopMoveManager()
    
    PopManager().add_pop_move_manager(pop_move_manager)

    # Initialize the world
    world = World()
    
    world.set_seed(seed)
    world.set_chunk_size(chunk_size)
    world.set_pop_move_manager(pop_move_manager)
    
    pop_move_manager.set_world(world)
    
    world.set_pop_move_manager(pop_move_manager)
    
    world.set_height(world_height)
    world.set_width(world_width)
    
    world.prepare()
    
    for i in range(initial_pop_count):
        world.add_pop_at((random.randint(0, world.width-1), random.randint(0, world.height-1)))

    return world

def main():
    world = prep_simulation()
    
    do_render = True # Set to True to render each step of the simulation to an image file

    run_simulation(world, max_iterations=1000, render=do_render, render_frequency=250)

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

