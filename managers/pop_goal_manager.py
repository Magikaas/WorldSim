from __future__ import annotations
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    import ai

class PopGoalManager:
    goals: List[ai.Goal]
    def __init__(self, pop):
        self.goals = []
        self.active_action = None
    
    def add_goal(self, goal):
        self.goals.append(goal)
    
    def perform_goals(self):
        for goal in self.goals:
            if goal.can_execute():
                goal.execute()
    
    def get_current_goal(self):
        if len(self.goals) > 0:
            for goal in self.goals:
                if not goal.is_fulfilled():
                    return goal
        else:
            return None
        
        return None
    
    def get_active_action(self):
        return self.active_action
    
    def set_active_action(self, action):
        self.active_action = action