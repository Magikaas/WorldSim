# This file contains the Blackboard class, which is a simple key-value store for sharing data between different parts of the AI system.
class Blackboard:
    def __init__(self):
        self._data = {}

    def get(self, key):
        return self._data.get(key)

    def set(self, key, value):
        self._data[key] = value