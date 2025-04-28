import os

import inspect
from managers.logger_manager import logger_manager
import obj.item.items
from obj.item import Item
from utils.logger import Logger

class ItemManager():
    items: dict[str, Item]
    def __init__(self):
        self.items = {}
        
        self.logger = Logger("itemmgr", logger_manager)
    
    def add_item(self, item):
        self.logger.debug(f'Adding item: {item.name}')
        self.items[item.name.lower()] = item
    
    def get_item(self, item_name) -> Item|None:
        return self.items.get(item_name)
    
    def remove_item(self, item_name):
        del self.items[item_name]
    
    def list_classes(self, module):
        classes = inspect.getmembers(module, inspect.isclass)
        return [cls for _, cls in classes]
    
    def register_items(self):
        for cls in self.list_classes(obj.item.items):
            if issubclass(cls, Item) and cls != Item:
                self.add_item(cls())
        
        # Register all items in the game_data/items folder
        for filename in os.listdir('game_data/items'):
            if filename.endswith('.json') and filename != '__init__.py':
                module_name = filename[:-3]
        

item_manager = ItemManager()