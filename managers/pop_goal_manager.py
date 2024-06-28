from __future__ import annotations
from typing import List, TYPE_CHECKING

from ai.goal import Goal, GoalPriority
from utils.logger import Logger

from managers.logger_manager import logger_manager

if TYPE_CHECKING:
    import ai
    import ai.goal

class PopGoalManager:
    goals: List[ai.goal.Goal]
    def __init__(self, pop):
        self.goals = []
        self.active_action = None
        self.pop = pop
        
        self.logger = Logger(pop.name + "_goal_manager", logger_manager)
    
    def add_goal(self, goal):
        self.goals.append(goal)
    
    def get_active_foreground_goal(self) -> Goal|None:
        for goal in self.goals:
            if goal.priority is not GoalPriority.BACKGROUND and not goal.is_fulfilled():
                return goal
        return None
    
    def perform_goals(self):
        current_goal = self.get_current_goal()
        passed_current_goal = False
        
        for goal in self.goals:
            # If we are past the current goal, and we find a new goal, we should not execute it.
            if current_goal is not None and passed_current_goal and goal is not current_goal:
                break
            
            # If a goal is already active, only start a new goal that is higher priority than the current goal
            if goal.can_execute():
                goal.execute()
                
                if goal is current_goal:
                    passed_current_goal = True
                else:
                    # We have a goal that is higher priority than the current goal, so we need to reset the currently active goal
                    if current_goal is not None:
                        current_goal.reset()
                break
    
    def get_current_goal(self) -> Goal|None:
        if len(self.goals) > 0:
            for goal in self.goals:
                if not goal.is_fulfilled():
                    return goal
        else:
            return None
        
        return None
    
    def get_pop_goals(self) -> List[ai.goal.Goal]:
        return self.goals