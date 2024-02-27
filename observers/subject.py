class Subject:
    def __init__(self):
        self.observers = []
    
    def register_observer(self, observer):
        self.observers.append(observer)
    
    def deregister_observer(self, observer):
        self.observers.remove(observer)
    
    def notify_observers(self):
        for observer in self.observers:
            observer.update(self)