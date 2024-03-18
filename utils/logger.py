class Logger:
    def __init__(self, name: str):
        self.name = name
    
    def log(self, message: str, *args):
        prefix = self.name.ljust(15)
        print(f"[{prefix}] {message}", *args)