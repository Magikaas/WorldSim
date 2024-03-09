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

    def get(self, action, entity, key):
        return self._data[entity.id][action.type].get(key)

    def set(self, entity, action, key, value):
        if self._data[entity.id] is None:
            self._data[entity.id] = {}
        
        if self._data[entity.id][action.type] is not None:
            self._data[entity.id][action.type][key] = {}
        
        self._data[entity.id][action.type][key] = value