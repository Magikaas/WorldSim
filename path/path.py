from path.popmove import PopMove

class Path:
    def __init__(self, pop):
        self.pop = pop
        self.moves = []
    
    def add_move(self, popmove: PopMove):
        self.moves.append(popmove)