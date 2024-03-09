from typing import List

from ai import Goal

class PopGoalManager:
    goals: List[Goal]
    def __init__(self, pop):
        self.goals = []
    
    def add_goal(self, goal):
        self.goals.append(goal)
    
    def perform_goals(self):
        for goal in self.goals:
            if goal.check_prep_conditions():
                goal.execute()
                if goal.check_post_conditions():
                    self.goals.remove(goal)