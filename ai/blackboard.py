from numpy import blackman
from utils.logger import Logger

# This file contains the Blackboard class, which is a simple key-value store for sharing data between different parts of the AI system.
class Blackboard:
    _instance = None
    
    def __init__(self):
        self._data = {}
        
        self.logger = Logger("blackboard")

    def get(self, key, entity=None, action=None):
        source = None
        
        if entity is None:
            source = self._data
        else:
            if entity.id in self._data:
                source = self._data[entity.id]
            else:
                source = self._data
        
        if action is not None:
            if action.name in source:
                action_source = source[action.name]
                if key in action_source:
                    source = action_source
        
        if source is None:
            return None
        
        return source.get(key)

    def set(self, key, value, entity=None, action=None):
        target = None
        
        if entity is None:
            target = self._data
        else:
            if entity.id not in self._data:
                self._data[entity.id] = {}
            target = self._data[entity.id]
        
        if action is not None:
            if action.type not in target:
                target[action.type] = {}
            target = target[action.type]
        
        target[key] = value
    
    def generate_data_key(self, resource):
        return ':'.join(["resource_location", resource.category, resource.name])
    
    def add_resource_location(self, resource, location):
        self.logger.debug("Adding resource '%s' at %s" % (resource.name, location))
        data_key = self.generate_data_key(resource)
        
        if data_key not in self._data:
            self._data[data_key] = []
        
        if location not in self._data[data_key]:
            self.logger.debug("Found resource '%s' at %s" % (resource.name, location))
            self._data[data_key].append(location)
    
    def remove_resource_location(self, resource, location):
        data_key = self.generate_data_key(resource)
        self._data[data_key].remove(location)
    
    def get_resource_location(self, resource):
        data_key = self.generate_data_key(resource)
        
        if data_key not in self._data:
            # If the specific resource can't be found, look for others of the same category
            data_key = ':'.join(["resource_location", resource.category])
            
            results = []
            
            for key in self._data:
                if key.startswith(data_key):
                    results += self._data[key]
        
        return self._data[data_key]

blackboard = Blackboard()