from utils.logger import Logger

# This file contains the Blackboard class, which is a simple key-value store for sharing data between different parts of the AI system.
class Blackboard:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Blackboard, cls).__new__(cls)
            
            cls._instance.__init__(**kwargs)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
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
            if action.type in source:
                action_source = source[action.type]
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
    
    def add_resource_location(self, resource, location):
        if "resource_location:" + resource.name not in self._data:
            self._data["resource_location:" + resource.name] = []
        
        if location not in self._data["resource_location:" + resource.name]:
            self.logger.log("Found resource '%s' at %s" % (resource.name, location))
            self._data["resource_location:" + resource.name].append(location)
    
    def remove_resource_location(self, resource, location):
        self._data["resource_location:" + resource.name].remove(location)
    
    def get_resource_location(self, resource):
        return self._data["resource_location:" + resource.name]