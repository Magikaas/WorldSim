import json
import os

from crafting.recipe import Recipe
from obj.item import ItemStack
from managers.logger_manager import logger_manager
from managers.item_manager import item_manager as ItemManager
from utils.logger import Logger


class RecipeManager():
    recipes: dict[str, Recipe]
    
    def __init__(self):
        self.recipes = {}
        
        self.logger = Logger("recipemgr", logger_manager)
    
    def add_recipe(self, recipe: Recipe):
        self.recipes[recipe.result.item.name.lower()] = recipe
    
    def get_recipe(self, item_name: str) -> Recipe:
        return self.recipes.get(item_name.lower())
    
    def remove_recipe(self, item_name: str):
        del self.recipes[item_name]
    
    def register_recipes(self):
        '''
        Register recipes from recipes.json file that contains a list of recipes
        Format of the file:
        {
            "recipes": [
                {
                    "materials": [
                        {
                            "item": "item_name",
                            "amount": 1
                        }
                    ],
                    "result": {
                        "item": "item_name",
                        "amount": 1
                    }
                }
            ]
        }
        '''
        
        recipe_file_output = {}
        
        # Load all files in the game_data/recipes folder
        # and register them as recipes
        for filename in os.listdir('game_data/recipes'):
            if filename.endswith('.json') and filename != '__init__.py':
                with open(f'game_data/recipes/{filename}', 'r') as file:
                    recipe = json.load(file)
                
                self.logger.debug(f'Loaded recipe from {filename}')
                
                materials = recipe['material']
                result = recipe['result']
                
                materials_list = []
                
                if not materials:
                    self.logger.error(f'No materials found for recipe {recipe}')
                    continue
                
                for material in materials:
                    item = ItemManager.get_item(material['item'])
                    
                    if not item:
                        self.logger.error(f'Material {material["item"]} not found for recipe {recipe}')
                        continue
                    
                    materials_list.append(ItemStack(item=item, amount=material['amount']))
                
                result_item = ItemManager.get_item(result['item'])
                
                if not result_item:
                    self.logger.error(f'Result {result["item"]} not found for recipe {recipe}')
                    continue
                
                result_item_stack = ItemStack(item=result_item, amount=result['amount'])
                
                self.add_recipe(Recipe(materials=materials_list, result=result_item_stack))
    
    def calculate_recipe(self, recipe: Recipe) -> dict[str, int]:
        '''
        Calculate the amount of each item needed for a recipe
        '''
        recipe_dict = {}
        
        for material in recipe.materials:
            item = material.item.name.lower()
            amount = material.amount
            
            if item in recipe_dict:
                recipe_dict[item] += amount
            else:
                recipe_dict[item] = amount
        
        return recipe_dict
    
    def __str__(self):
        return f'<RecipeManager: {self.recipes}>'

recipe_manager = RecipeManager()