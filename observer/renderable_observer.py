from .observer import Observer

class RenderableObserver(Observer):
    def update(self, subject):
        subject.dirty = True