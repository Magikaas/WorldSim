class Pop:
    def __init__(self, id, role='worker', health=100, age=0, skills=None, x=0, y=0):
        self.id = id
        self.role = role
        self.health = health
        self.age = age
        self.skills = skills if skills else {}
        self.x = x
        self.y = y
    
    def update(self):
        # Update logic for aging, health changes, skill improvements, etc.
        self.age += 1