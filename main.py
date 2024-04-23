import cProfile
import pstats
import pygame
import random
import os
import io
import time

# examples/generate_world.py
from managers.logger_manager import LoggerManager
from world.world import world, World
from managers.pop_manager import pop_manager as PopManager
from managers.pop_move_manager import pop_move_manager as PopMoveManagerInstance

from utils.renderoutput import RenderOutput

from utils.logger import Logger

import os
    
logger = Logger("general")

def run_simulation(world: World, max_iterations=1000, render=False, render_frequency=1000):
    step_nr = 0
    
    sim_seed = world.seed
    
    scale = 2
    
    show_location = False
    show_status = False
    show_goals = False
    show_items = False
    
    pygame.init()
    
    logger.debug("=====================================")
    logger.debug("Starting simulation")
    logger.debug("=====================================")
    
    if render:
        clock = pygame.time.Clock()
        
        width = world.get_size()[0]
        height = world.get_size()[1]
        
        world_size = (width * scale, height * scale)
        
        window = pygame.display.set_mode(world_size)
        
        surface = pygame.Surface(world_size)
    
    font = pygame.font.SysFont('robotoregular', 16)
    world.font = font
    # clear = lambda: os.system('cls')
    
    paused = False
    
    for iteration in range(max_iterations):
        # clear()
        if render:
            pygame.event.get()
            # clock.tick(15)
        
        step_nr += 1
        
        if render:
            surface = world.render(surface=surface, scale=scale, output=RenderOutput.VARIABLE)
            
            screen_width = world.width * scale / 2
            screen_height = world.height * scale / 2
            
            window.fill(0)
            window.blit(surface, surface.get_rect(center = (screen_width, screen_height)))
            # pygame.display.flip()
            
            if step_nr % render_frequency == 0:
                str_seed = str(sim_seed)
                
                # if a folder does not exist, create it
                filename = "output/" + str_seed + "/" + str(world.width) + "x" + str(world.height) + "_scale_" + str(scale) + "_" + str(step_nr) + ".png"
                
                if os.path.exists("output") == False:
                    os.mkdir("output")
                
                if os.path.exists("output/" + str_seed) == False:
                    os.mkdir("output/" + str_seed)
                
                logger.info("Writing map file to ", filename)
                
                surface = world.render(surface=surface, scale=scale, output=RenderOutput.FILE, filename=filename)
            
            # Show state of each pop on screen
            for pop in PopManager.get_pops():
                if show_location:
                    pop_location = pop.location
                    pop_location = (pop_location[0] * scale, pop_location[1] * scale)
                    
                    text = font.render(pop.state, True, (255, 255, 255))
                    
                    window.blit(text, pop_location)
                
                if show_goals:
                    # Show the pop's current goal
                    goal = pop.get_current_goal()
                    
                    goal_location = (pop_location[0], pop_location[1] + 20)
                    
                    goal_string = str(goal.type) if goal is not None else "None"
                    
                    goal_text = font.render(goal_string, True, (255, 255, 255))
                    
                    window.blit(goal_text, goal_location)
                
                if show_status:
                    # Show the pop's status
                    pop_status_text = font.render(f"Health: {pop.health}, Food: {pop.food}, Water: {pop.water}", True, (255, 255, 255))
                    
                    pop_status_text_location = (pop_location[0], pop_location[1] + 20)
                    
                    window.blit(pop_status_text, pop_status_text_location)
                
                if show_items:
                    # Show the pop's inventory
                    inventory = pop.inventory
                    
                    x = 40
                    
                    items = inventory.items
                    
                    for item_name in items:
                        inventory_location = (pop_location[0], pop_location[1] + x)
                        
                        inventory_text = font.render(str(items[item_name]), True, (255, 255, 255))
                        
                        window.blit(inventory_text, inventory_location)
                        
                        x += 20
                
                # Render the new frame completely
                pygame.display.flip()
        
        if iteration % render_frequency == 0:
            logger.info(f"Iteration {iteration}. Time millis: {pygame.time.get_ticks()}. Pops: {len(PopManager.get_pops())}")
            print(f"Iteration {iteration}. Time millis: {pygame.time.get_ticks()}. Pops: {len(PopManager.get_pops())}")
        
        # Update the world state, which includes updating all pops within it
        if not paused:
            world.update()

        if check_end_conditions(world) and False:
            logger.info(f"Simulation ended at iteration {iteration}")
            break

        # Example: You could add new pops or change the world based on specific conditions
        # if iteration % 100 == 0:
            # world.add_pop(new_pop)

def check_end_conditions(world):
    return len(PopManager.get_pops()) == 0 or world_reached_goal(world)

def world_reached_goal(world: World):
    # Define the conditions for what it means for the world to have "reached its goal"
    if len(PopManager.get_pops()) > 1000:
        return True
    return False  # Placeholder logic

def prep_simulation():
    size = 128
    world_width = size
    world_height = size
    initial_pop_count = 25
    seed = 1010
    chunk_size = 16
    
    # np.random.seed(hash(seed) % 2**32)
    
    pop_move_manager = PopMoveManagerInstance
    
    PopManager.add_pop_move_manager(pop_move_manager)

    # Initialize the world
    world.seed = seed
    world.set_chunk_size(chunk_size)
    world.pop_move_manager = pop_move_manager
    
    pop_move_manager.world = world
    
    world.height = world_height
    world.width = world_width
    
    world.prepare()
    
    for i in range(initial_pop_count):
        world.add_pop_at((random.randint(0, world.width-1), random.randint(0, world.height-1)))

    return world

def main():
    world = prep_simulation()
    
    max_iterations = 10000
    render_frequency = 250
    
    do_render = True # Set to True to render each step of the simulation to an image file

    run_simulation(world, max_iterations=max_iterations, render=do_render, render_frequency=render_frequency)

    logger.info("Simulation complete")

profile = True # Profile the code using cProfile
if __name__ == "__main__":
    if profile:
        profiler = cProfile.Profile()
        profiler.enable()
        main()
        profiler.disable()
        # stats = pstats.Stats(profiler).sort_stats('cumtime')
        
        s = io.StringIO()
        
        timestamp = str(int(time.time()))
        
        for logger in LoggerManager.loggers.values():
            logger.flush_messages()
        
        # stats.print_stats()
        with open("profile/" + timestamp + ".txt", "w") as f:
            stats = pstats.Stats(profiler, stream=f).sort_stats('cumtime')
            print("Printing stats")
            stats.print_stats()
            print("Finished printing stats")
    else:
        main()

