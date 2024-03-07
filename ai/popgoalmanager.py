from typing import List

from ai import Goal

class PopGoalManager:
    goals: List[Goal]
    def __init__(self):
        self.goals = []
    
    def add_goal(self, goal):
        self.goals.append(goal)
    
    def check_goals(self):
        for goal in self.goals:
            if goal.check_conditions():
                return goal
        return None