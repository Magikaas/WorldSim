import json

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
        self.recipes[recipe.result.item.name] = recipe
    
    def get_recipe(self, item_name: str) -> Recipe:
        return self.recipes.get(item_name)
    
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
        with open('recipes.json', 'r') as file:
            recipe_file_output = json.load(file)
        
        self.logger.debug(f'Loaded recipes count: {len(recipe_file_output["recipes"])}')
        
        for recipe in recipe_file_output['recipes']:
            materials = recipe['materials']
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
    
    def __str__(self):
        return f'<RecipeManager: {self.recipes}>'

recipe_manager = RecipeManager()