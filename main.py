import cProfile
import pstats
import pygame
import random
import os
import io
import time
import json
import tkinter as tk

from managers.logger_manager import logger_manager
from world.world import world, World
from managers.pop_manager import pop_manager as PopManager
from managers.pop_move_manager import pop_move_manager as PopMoveManagerInstance
from managers.recipe_manager import recipe_manager as RecipeManager
from managers.item_manager import item_manager as ItemManager

from utils.renderoutput import RenderOutput

from utils.logger import Logger

logger = Logger("general", logger_manager)

with open("config.json", "r") as f:
    config = json.load(f)

def run_simulation(world: World, max_simulation_steps=1000, render=False, render_frequency=1000):
    step_nr = 0
    
    sim_seed = world.seed

    root = tk.Tk()
    screen_height = root.winfo_screenheight()
    root.destroy()
    
    scale = screen_height / world.width
    scale = scale - (scale % 1)
    
    show_tooltip = True
    
    show_location = True
    show_status = True
    show_goals = True
    show_items = True
    
    pygame.init()
    
    logger.debug("=====================================", printMessage=True)
    logger.debug("Starting simulation", printMessage=True)
    logger.debug("=====================================", printMessage=True)
    logger.debug("World size: %s x %s" % (world.width, world.height), printMessage=True)
    logger.debug("World scale: %s" % (scale), printMessage=True)
    logger.debug("World seed: %s" % (world.seed), printMessage=True)
    logger.debug("World chunk size: %s" % (world.chunk_size), printMessage=True)
    logger.debug("Initial pop count: %s" % (len(PopManager.get_pops())), printMessage=True)
    logger.debug("======================================", printMessage=True)
    
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
    
    while True:
        keys = pygame.key.get_just_released()
        
        if keys[pygame.K_SPACE]:
            paused = not paused
        
        if keys[pygame.K_q]:
            break
        
        if keys[pygame.K_l]:
            show_location = not show_location
        
        if keys[pygame.K_s]:
            show_status = not show_status
            
        if keys[pygame.K_g]:
            show_goals = not show_goals
            
        if keys[pygame.K_i]:
            show_items = not show_items
            
        if keys[pygame.K_p]:
            for pop in PopManager.get_pops():
                pop.health = 0
                
        if keys[pygame.K_o]:
            for pop in PopManager.get_pops():
                pop.food = 0
                # pop.water = 0
        
        # clear()
        if render:
            pygame.event.get()
            # clock.tick(config["sim_fps"])
        
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
                
                logger.info("Writing map file to ", filename, printMessage=True)
                
                surface = world.render(surface=surface, scale=scale, output=RenderOutput.FILE, filename=filename)
            
            if show_tooltip:
                tooltip_width = 300
                
                text_offset = 0
                
                # Show state of each pop on screen
                for pop in PopManager.get_pops():
                    tooltip_height = 0
                    
                    pop_location = pop.location
                    pop_location = (pop_location[0] * scale, pop_location[1] * scale)
                    
                    text_offset = 0
                    
                    if show_goals:
                        tooltip_height += 20
                    
                    if show_status:
                        tooltip_height += 20
                    
                    if show_items:
                        inventory = pop.inventory
                            
                        items = inventory.items
                        
                        tooltip_height += 20 * len(items)
                    
                    if show_location:
                        tooltip_height += 20
                    
                    if text_offset > tooltip_height:
                        tooltip_height = text_offset
                    
                    tooltip_height += 5
                    
                    text_offset = 0
                    
                    # Render the tooltip
                    tooltip_location = (pop_location[0] - 5, pop_location[1] - 5)
                    
                    pygame.draw.rect(window, (0, 0, 0), (tooltip_location[0], tooltip_location[1], tooltip_width, tooltip_height))
                    
                    if show_location:
                        text = font.render(pop.name, True, (255, 255, 255))
                        
                        window.blit(text, pop_location)
                        
                        text_offset += 20
                    
                    if show_goals:
                        # Show the pop's current goal
                        goal = pop.get_current_goal()
                        
                        goal_location = (pop_location[0], pop_location[1] + text_offset)
                        
                        goal_string = "Goal: " + (str(goal.type) if goal is not None else "None") + " - Tries: " + str(goal.tries) if goal is not None else "None"
                        
                        goal_text = font.render(goal_string, True, (255, 255, 255))
                        
                        window.blit(goal_text, goal_location)
                        
                        text_offset += 20
                    
                    if show_status:
                        # Show the pop's status
                        pop_status_text = font.render(f"Health: {pop.health}, Food: {pop.food}, Water: {pop.water}", True, (255, 255, 255))
                        
                        pop_status_text_location = (pop_location[0], pop_location[1] + text_offset)
                        
                        window.blit(pop_status_text, pop_status_text_location)
                        
                        text_offset += 20
                    
                    if show_items:
                        # Show the pop's inventory
                        inventory = pop.inventory
                        
                        items = inventory.items
                        
                        for item_name in items:
                            inventory_location = (pop_location[0], pop_location[1] + text_offset)
                            
                            inventory_text = font.render(str(items[item_name]), True, (255, 255, 255))
                            
                            window.blit(inventory_text, inventory_location)
                        
                            text_offset += 20
                    
            # Render the new frame completely
            pygame.display.flip()
        
        if step_nr % render_frequency == 0:
            logger.info(f"Step {step_nr}. Time millis: {pygame.time.get_ticks()}. Pops: {len(PopManager.get_pops())}")
            print(f"Step {step_nr}. Time millis: {pygame.time.get_ticks()}. Pops: {len(PopManager.get_pops())}")
        
        # Update the world state, which includes updating all pops within it
        if not paused:
            world.update()

        if check_end_conditions(world) and False:
            logger.info(f"End conditions reached at step {step_nr}")
            break
        
        if step_nr >= max_simulation_steps:
            logger.info(f"Simulation ended at step {step_nr}")
            break
        
        if not paused:
            step_nr += 1
            logger_manager.sim_step = step_nr
        
        # break

def check_end_conditions(world):
    return len(PopManager.get_pops()) == 0 or world_reached_goal(world)

def world_reached_goal(world: World):
    # Define the conditions for what it means for the world to have "reached its goal"
    if len(PopManager.get_pops()) > 1000:
        return True
    return False  # Placeholder logic

def prep_simulation():
    size = config["world_size"]
    world_width = size
    world_height = size
    initial_pop_count = config["initial_pop_count"]
    seed = config["seed"]
    chunk_size = config["chunk_size"]
    
    # Import all recipes from the recipes.json file
    ItemManager.register_items()
    RecipeManager.register_recipes()
    
    # Generate worlds in different sizes to test the performance of the world generation algorithm
    
    world = prep_world(world_width, world_height, initial_pop_count, seed, chunk_size)

    return world

def prep_world(width, height, initial_pop_count, seed, chunk_size):
    pop_move_manager = PopMoveManagerInstance
    
    PopManager.add_pop_move_manager(pop_move_manager)

    # Initialize the world
    world.seed = seed
    world.set_chunk_size(chunk_size)
    world.pop_move_manager = pop_move_manager
    
    pop_move_manager.world = world
    
    world.height = height
    world.width = width
    
    world.prepare()
    
    for i in range(initial_pop_count):
        world.add_pop_at((random.randint(20, world.width-21), random.randint(20, world.height-21)))
    
    return world

def main():
    world = prep_simulation()
    
    max_simulation_steps = config["max_simulation_steps"]
    render_frequency = config["render_frequency"]
    
    do_render = True # Set to True to render each step of the simulation to an image file

    run_simulation(world, max_simulation_steps=max_simulation_steps, render=do_render, render_frequency=render_frequency)

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
        
        for logger in logger_manager.loggers.values():
            logger.flush_messages()
        
        # stats.print_stats()
        with open("profile/" + timestamp + ".txt", "w") as f:
            stats = pstats.Stats(profiler, stream=f).sort_stats('cumtime')
            print("Printing stats")
            stats.print_stats()
            print("Finished printing stats")
    else:
        main()

