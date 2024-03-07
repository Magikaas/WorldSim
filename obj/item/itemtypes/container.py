class Container:
    def __init__(self, capacity=0, contents=None):
        self.capacity = capacity
        self.contents = contents or []

    def add(self, item):
        if len(self.contents) < self.capacity:
            self.contents.append(item)
            return True
        return False

    def remove(self, item):
        if item in self.contents:
            self.contents.remove(item)
            return True
        return False

    def __iter__(self):
        return iter(self.contents)

    def __len__(self):
        return len(self.contents)

    def __contains__(self, item):
        return item in self.contents

    def __getitem__(self, index):
        return self.contents[index]

    def __setitem__(self, index, value):
        self.contents[index] = value

    def __delitem__(self, index):
        del self.contents[index]

    def __repr__(self):
        return f'<Container: {self.contents}>'

    def __str__(self):
        return f'<Container: {self.contents}>'