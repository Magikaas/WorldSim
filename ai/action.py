from enum import Enum
from abc import ABC, abstractmethod

from crafting.recipe import Recipe
from managers.logger_manager import logger_manager
from obj import item
from obj.item import Item, ItemStack, ItemCategory
from obj.item.item import BareHands, Tool
from obj.worldobj.entity import Entity, EntityState
from obj.worldobj.building import Building

from ai.condition import Condition, OnLocationCondition, HasItemsCondition, BuildingExistsCondition, BlackboardContainsLocationCondition
from ai.blackboard import blackboard as Blackboard
from managers.recipe_manager import recipe_manager as RecipeManager

from managers.pop_manager import pop_manager as PopManager
from managers.pop_move_manager import pop_move_manager as PopMoveManagerInstance

from obj.worldobj.resourcenode import NoResource
from object_types import Location
from utils.logger import Logger
from world.tile import Tile

class ActionState(Enum):
    INACTIVE = 0
    ACTIVE = 1
    DONE = 2

class Action(ABC):
    def __init__(self, name: str, entity: Entity, parent_action=None):
        # self.logger.debug("Initialising action %s for entity %s" % (name, entity.name))
        self.name = name
        self.parent_action = parent_action
        
        self.logger = Logger("ActionType.%s" % name.upper(), logger_manager)
        
        self.pop_state = None
        
        self.conditions = {"prep": [], "post": []}
        
        self.retries = 0
        
        self.state = ActionState.INACTIVE
        
        self.entity = PopManager.get_pop(entity.id)
        
        self.required_tools = []
        
        self.determine_conditions()
        
        self.determine_actions()
    
    def __str__(self):
        return self.name
    
    def deactivate(self):
        self.logger.debug("Deactivating action %s" % self, actor=self.entity)
        self.state = ActionState.INACTIVE
    
    def activate(self):
        self.logger.debug("Activating action %s" % self, actor=self.entity)
        self.state = ActionState.ACTIVE
        # self.logger.custom("Action %s:%s activated" % (self.name, hash(self)), actor=self.entity, level_name="ACTION_ACTIVATED")
    
    def is_active(self):
        return self.state == ActionState.ACTIVE
    
    def reset(self):
        self.logger.debug("Resetting action %s" % self, actor=self.entity)
        
        self.conditions = {"prep": [], "post": []}
        self.deactivate()
        self.retries = 0
        self.determine_conditions()
        self.determine_actions()
    
    def finish(self):
        self.logger.debug("Finishing action %s" % self, actor=self.entity, printMessage=False)
        self.state = ActionState.DONE
        # self.logger.custom("Action %s:%s finished" % (self.name, hash(self)), actor=self.entity, level_name="ACTION_FINISHED")
    
    def is_finished(self):
        return self.state == ActionState.DONE
    
    def get_closest_tile_with_resource(self, location: Location|str) -> Tile|None:
        world = self.entity.world
        locations = []
        
        if isinstance(location, str) and location.startswith("resource_location:"):
            locations = Blackboard.get(entity=self.entity, action=self.parent_action, key=location)
            location = ""
        
        if locations is not None and len(locations) > 0:
            closest_location = world.find_closest_location(self.entity.location, locations, self.entity)
            
            if closest_location is not None:
                location = closest_location
        
        if location == "" or location is None:
            self.logger.debug("No location found", actor=self.entity)
            return None
        
        destination_tile = world.get_tile(location)
        
        return destination_tile
    
    def execute(self):
        if self.is_finished():
            self.logger.debug("Action %s is already finished" % self, actor=self.entity)
            return True
        
        self.logger.debug("Entity %s is executing action %s" % (self.entity.name, self.name))
        
        self.retries += 1
        
        if not self.is_active() and not self.is_finished() and not self.check_prep_conditions():
            if self.retries > 5:
                if self.check_post_conditions():
                    self.finish()
                    return True
                
                if self.retries > 15:
                    self.logger.error("Failed to execute action %s after %s retries" % (self.name, self.retries), actor=self.entity)
                    self.logger.debug("Action %s failed to execute - Reason: %s" % (self, self.get_failed_post_conditions()), actor=self.entity)
                    self.reset()
            return False
        
        if self.is_active():
            return self.update()
        
        self.activate()
        
        result = self.start()
        
        if result == True:
            self.finish()
        
        return result
    
    def has_subactions(self):
        return False
    
    def check_prep_conditions(self) -> bool:
        for condition in self.conditions["prep"]:
            if condition.check_condition() == False:
                self.logger.debug("Pre condition %s for action %s failed" % (condition.type, self), actor=self.entity)
                return False
        return True
    
    def check_post_conditions(self) -> bool:
        for condition in self.conditions["post"]:
            if condition.check_condition() == False:
                self.logger.debug("Post condition %s for action %s failed" % (condition.type, self), actor=self.entity)
                return False
        return True
    
    def get_failed_prep_conditions(self) -> list[Condition]:
        failed_conditions = []
        
        for condition in self.conditions["prep"]:
            if not condition.check_condition():
                failed_conditions.append(condition)
        
        return failed_conditions
    
    def get_failed_post_conditions(self) -> list[Condition]:
        failed_conditions = []
        
        for condition in self.conditions["post"]:
            if not condition.check_condition():
                failed_conditions.append(condition)
        
        return failed_conditions
    
    def add_prep_condition(self, condition: Condition):
        self.conditions["prep"].append(condition)
    
    def add_post_condition(self, condition: Condition):
        self.conditions["post"].append(condition)
    
    def determine_actions(self):
        pass
    
    def determine_conditions(self):
        pass
    
    @abstractmethod
    def start(self) -> bool: ...
    
    @abstractmethod
    def update(self) -> bool: ...

class CompositeAction(Action):
    actions: list[Action]
    
    def __init__(self, name: str, entity: Entity, parent_action=None):
        self.actions = []
        
        super().__init__(name=name, entity=entity, parent_action=parent_action)
    
    def add_action(self, action: Action):
        self.actions.append(action)
    
    def start(self) -> bool:
        if not self.is_active():
            self.activate()
        return self.check_post_conditions()
    
    def get_active_action(self) -> Action|None:
        for action in self.actions:
            if action.is_active():
                return action
        return None
    
    def update(self) -> bool:
        result = True
        
        self.logger.debug("Updating composite action %s" % self, actor=self.entity)
        
        for action in self.actions:
            if action.is_finished():
                continue
            else:
                result = False
            
            if action.is_active():
                action.update()
                
                if action.is_finished():
                    continue
                break
            else:
                result = action.execute()
        
        if result:
            self.finish()
        return result
    
    def has_subactions(self):
        return len(self.actions) > 0

class MoveAction(Action):
    def __init__(self, entity: Entity, location: Location|str, parent_action: CompositeAction|None = None):
        self.location = location
        
        super().__init__(name="move", entity=entity, parent_action=parent_action)
        
        self.logger.debug("Creating move action to location %s" % str(location), actor=entity)
    
    def __str__(self):
        return super().__str__() + ":" + str(self.location)
    
    def determine_conditions(self):
        self.add_prep_condition(OnLocationCondition(entity_id=self.entity.id, location=self.location).invert())
        self.add_post_condition(OnLocationCondition(entity_id=self.entity.id, location=self.location))
    
    def start(self):
        parent_action_actions = self.parent_action.actions if self.parent_action is not None else []
        
        world = self.entity.world
        
        if len(parent_action_actions) > 0:
            for action in parent_action_actions:
                if isinstance(action, LocateResourceAction):
                    destination_tile = action.target_tile
                    break
        else:
            destination_tile = self.get_closest_tile_with_resource(location=self.location)
            
        if destination_tile is None:
            return False
        
        path = world.pathfind(pop=self.entity, target_location=destination_tile.location)
        
        PopMoveManagerInstance.empty_moves(self.entity)
        
        for move in path.moves:
            PopMoveManagerInstance.move_pop(move)
        
        return False # We need to wait for the pop to move
    
    def update(self):
        move = PopMoveManagerInstance.get_move_for_pop(self.entity)
        
        if move is None:
            self.finish()
            return False
        
        return True

class BuildAction(Action):
    def __init__(self, entity: Entity, building: Building, target_tile, parent_action: CompositeAction|None = None):
        self.building = building
        self.pop_state = EntityState.BUILDING
        self.target_tile = target_tile
        
        super().__init__(name="build", entity=entity, parent_action=parent_action)
    
    def __str__(self):
        return super().__str__() + ":" + str(self.target_tile) + ":" + self.building.name
    
    def is_done(self):
        return self.entity.state == EntityState.IDLE
    
    def determine_conditions(self):
        if len(self.building.materials) > 0:
            for m in self.building.materials:
                self.add_prep_condition(HasItemsCondition(entity_id=self.entity.id, item=m))
        
        self.add_prep_condition(BuildingExistsCondition(building=self.building, target_tile=self.target_tile).invert())
        self.add_post_condition(BuildingExistsCondition(building=self.building, target_tile=self.target_tile))
    
    def start(self):
        self.logger.info("Building %s with %s" % (self.building.name, ', '.join([item.item.name + "x" + str(item.amount) for item in self.building.materials])), actor=self.entity)
        return False # The building is not built yet
    
    def update(self):
        # TODO: Make building take time
        
        world = self.entity.world
        tile = world.get_tile(self.entity.location)
        
        tile.build(self.building, self.entity)
        
        if tile.has_building() and tile.building == self.building:
            self.finish()
            return True
        
        return False

class LocateResourceAction(Action):
    def __init__(self, entity: Entity, resource: Item, parent_action: CompositeAction|None = None):
        self.resource = resource
        self.target_tile = None
        
        self.pop_state = EntityState.SEARCHING
        
        super().__init__(name="locate_resource", entity=entity, parent_action=parent_action)
    
    def __str__(self):
        return super().__str__() + ":" + self.resource.name
    
    def determine_conditions(self):
        # Check if the blackboard has a location for the resource
        max_distance = int(self.entity.world.width / 4)
        self.add_prep_condition(BlackboardContainsLocationCondition(resource=self.resource, entity_id=self.entity.id, max_distance=max_distance).invert())
        self.add_post_condition(BlackboardContainsLocationCondition(resource=self.resource, entity_id=self.entity.id, max_distance=max_distance))
    
    def start(self):
        world = self.entity.world
        
        resource_tiles = world.find_tiles_with_resource_near(location=self.entity.location, resource_type=self.resource, distance=15)
        
        self.shortest_path_length = 1000
        
        for tile in resource_tiles:
            distance = abs(self.entity.location[0] - tile.location[0]) + abs(self.entity.location[1] - tile.location[1])
            
            Blackboard.add_resource_location(resource=self.resource, location=tile.location)
            
            if distance < self.shortest_path_length:
                self.shortest_path_length = distance
                self.target_tile = tile
        
        return self.target_tile is not None
    
    def update(self):
        target_tile = self.target_tile
        world = self.entity.world
        
        search_distance = 5
        
        if target_tile is not None:
            # Add the tile to the blackboard for later actions
            Blackboard.add_resource_location(resource=self.resource, location=target_tile.location)
        else:
            while target_tile is None and search_distance < 45:
                search_distance += 5
                resource_tiles = world.find_tiles_with_resource_near(location=self.entity.location, resource_type=self.resource, distance=search_distance)
                
                for tile in resource_tiles:
                    Blackboard.add_resource_location(resource=self.resource, location=tile.location)
                    
                    path = world.pathfind(pop=self.entity, target_location=tile.location)
                    
                    if (len(path.moves) < self.shortest_path_length) or target_tile is None:
                        self.shortest_path_length = len(path.moves)
                        target_tile = tile
            
            if target_tile is not None:
                Blackboard.add_resource_location(resource=self.resource, location=target_tile.location)
            else:
                # self.logger.warn("Found no resource tiles for %s near location %s" % (self.resource.name, str(self.entity.location)), actor=self.entity)
                return False
        
        self.target_tile = target_tile
        
        self.finish()

class HarvestAction(Action):
    def __init__(self, entity: Entity, gather_tool: Tool|None = None, amount:int = 0, parent_action: CompositeAction|None = None):
        super().__init__(name="harvest", entity=entity, parent_action=parent_action)
        
        self.amount = amount
        self.pop_state = EntityState.GATHERING
        self.gather_tool = gather_tool
    
    def __str__(self):
        return super().__str__() + ":" + str(self.amount)
    
    def start(self):
        world = self.entity.world
        
        location = self.entity.location
        
        tile = world.get_tile(location)
        
        resourcenode = tile.resourcenode
        
        if type(resourcenode) == type(NoResource()):
            self.logger.warn("No resource node found at location %s" % str(location), actor=self.entity)
            return False
        else:
            self.logger.debug("Harvesting resource %s from node %s" % (resourcenode.harvestable_resource.name, resourcenode.name), actor=self.entity)
        
        item = resourcenode.harvestable_resource
        
        # Do checks to see if the pop can harvest the resource with the tool they have
        if item.harvest_tool is not None and self.gather_tool is not None and self.gather_tool != BareHands() and item.harvest_tool != self.gather_tool:
            self.logger.warn("Pop does not have the required tool %s to harvest resource %s" % (item.harvest_tool, item.name), actor=self.entity)
            return False
        
        item_stack = resourcenode.harvest(self.amount)
        
        PopManager.give_item_to_pop(pop=self.entity, item=item_stack)
    
    def update(self):
        # TODO: Make harvesting take time
        if self.entity.state == EntityState.IDLE:
            self.finish()
            return True
        
        return False

class GatherAction(CompositeAction):
    def __init__(self, entity: Entity, target_item: ItemStack, gather_tool: Tool|None = None, parent_action: CompositeAction|None = None):
        self.resource = target_item
        self.pop_state = EntityState.GATHERING
        self.gather_tool = gather_tool
        
        super().__init__(name="gather", entity=entity, parent_action=parent_action)
    
    def __str__(self):
        return super().__str__() + ":" + str(self.resource)
    
    def determine_conditions(self):
        self.add_prep_condition(HasItemsCondition(entity_id=self.entity.id, item=self.resource).invert())
        self.add_post_condition(HasItemsCondition(entity_id=self.entity.id, item=self.resource))
    
    def determine_actions(self):
        item = self.resource.item if isinstance(self.resource, ItemStack) else self.resource
        amount = self.resource.amount if isinstance(self.resource, ItemStack) else self.resource
        
        # If the item is a tool, we need to craft it, instead of gathering it
        if item.category == ItemCategory.TOOL:
            recipe = RecipeManager.get_recipe(item.name)
            if recipe is None:
                self.logger.error("No recipe found for %s" % item.name, actor=self.entity)
                self.logger.debug("No recipe found for %s" % item.name, actor=self.entity)
                return
            
            self.add_action(CraftCompositeAction(entity=self.entity, recipe=recipe, parent_action=self))
        # Else, we need to locate the resource, move to it, and harvest it
        else:
            resource_key = ':'.join(["resource_location", item.category, item.name]) if isinstance(item, Item) else type(item)
            
            self.add_action(LocateResourceAction(entity=self.entity, resource=item, parent_action=self))
            
            if self.gather_tool is not None and self.gather_tool != BareHands():
                self.add_action(GuaranteeRequiredToolsAction(entity=self.entity, parent_action=self))
            
            self.add_action(MoveAction(entity=self.entity, location=resource_key, parent_action=self))
            self.add_action(HarvestAction(entity=self.entity, gather_tool=self.gather_tool, amount=amount, parent_action=self))
    
    def start(self) -> bool:
        return super().start()
    
    def update(self) -> bool:
        return super().update()

class CraftCompositeAction(CompositeAction):
    def __init__(self, name: str, entity: Entity, recipe: Recipe, parent_action: CompositeAction|None = None):
        self.recipe = recipe
        self.pop_state = EntityState.CRAFTING
        
        super().__init__(name=name, entity=entity, parent_action=parent_action)
    
    def __str__(self):
        return super().__str__() + ":" + str(self.recipe)
    
    def determine_actions(self):
        for item in self.recipe.materials:
            self.add_action(GatherAction(entity=self.entity, target_item=item, parent_action=self))
        
        self.add_action(CraftAction(entity=self.entity, recipe=self.recipe, parent_action=self))
    
    def determine_conditions(self):
        self.add_prep_condition(HasItemsCondition(entity_id=self.entity.id, item=self.recipe.result).invert())
        self.add_post_condition(HasItemsCondition(entity_id=self.entity.id, item=self.recipe.result))

class CraftAction(Action):
    def __init__(self, entity: Entity, recipe: Recipe, parent_action: CompositeAction|None = None):
        self.recipe = recipe
        
        super().__init__(name="craft", entity=entity, parent_action=parent_action)
        
        self.pop_state = EntityState.CRAFTING
    
    def __str__(self):
        return super().__str__() + ":" + str(self.recipe)
    
    def determine_conditions(self):
        for item in self.recipe.materials:
            self.add_prep_condition(HasItemsCondition(entity_id=self.entity.id, item=item))
    
    def start(self):
        self.logger.debug("Crafting %s" % (self.recipe.result.item.name), actor=self.entity)
        
        self.entity.state = self.pop_state
        
        # TODO: Add time to crafting
        
        self.entity.craft(self.recipe)
        
        self.logger.info("Crafted %s" % (self.recipe.result.item.name), actor=self.entity, printMessage=False)
        
        return True
    
    def update(self):
        return False

class DrinkAction(Action):
    def __init__(self, entity: Entity, parent_action: CompositeAction|None = None):
        super().__init__(name="drink", entity=entity, parent_action=parent_action)
    
    def start(self):
        tile = self.entity.world.get_tile(self.entity.location)
        
        resourcenode = tile.resourcenode
        
        water = resourcenode.harvestable_resource
        
        # self.entity.drink(water)

class GuaranteeRequiredToolsAction(CompositeAction):
    def __init__(self, entity: Entity, parent_action: CompositeAction|None = None):
        super().__init__(name="guarantee_required_tools", entity=entity, parent_action=parent_action)
    
    def __str__(self):
        return super().__str__() + ":" + str(self.required_tools)
    
    def start(self):
        super().start()
    
    def determine_conditions(self):
        for tool in self.required_tools:
            item = ItemStack(tool, 1)
            self.add_prep_condition(HasItemsCondition(entity_id=self.entity.id, item=item).invert())
            self.add_post_condition(HasItemsCondition(entity_id=self.entity.id, item=item))
    
    def determine_actions(self):
        if self.required_tools is None or len(self.required_tools) == 0:
            self.determine_required_tools()
        
        for tool in self.required_tools:
            item = ItemStack(tool, 1)
            self.add_action(GatherAction(entity=self.entity, target_item=item, parent_action=self))
    
    def determine_required_tools(self):
        parent_action = self.parent_action
        parent_action_actions = parent_action.actions if parent_action is not None else []
        
        if len(parent_action_actions) == 0:
            self.logger.warn("Parent action has no actions", actor=self.entity)
            return
        
        required_tools = []
        
        for action in parent_action_actions:
            if isinstance(action, LocateResourceAction):
                target_tile = action.target_tile
                
                if target_tile is None:
                    continue
                
                resourcenode = target_tile.resourcenode
                
                if resourcenode is None:
                    continue
                
                tool = resourcenode.harvest_tool
                
                if tool is not None:
                    required_tools.append(tool)
                
                break
        
        self.required_tools = required_tools


####################### HARDCODED CRAFTING ACTIONS #######################

class CraftAxeAction(CraftCompositeAction):
    def __init__(self, entity: Entity, parent_action: CompositeAction|None = None):
        recipe = RecipeManager.get_recipe("axe")
        
        super().__init__(name="craft_axe_action", entity=entity, recipe=recipe, parent_action=parent_action)
    
    def determine_actions(self):
        for item in self.recipe.materials:
            self.add_action(GatherAction(entity=self.entity, target_item=item, gather_tool=BareHands(), parent_action=self))
        
        self.add_action(CraftAction(entity=self.entity, recipe=self.recipe, parent_action=self))

class CraftPickaxeAction(CraftCompositeAction):
    def __init__(self, entity: Entity, parent_action: CompositeAction|None = None):
        recipe = RecipeManager.get_recipe("pickaxe")
        
        super().__init__(name="craft_pickaxe_action", entity=entity, recipe=recipe, parent_action=parent_action)
    
    def determine_actions(self):
        for item in self.recipe.materials:
            self.add_action(GatherAction(entity=self.entity, target_item=item, gather_tool=BareHands(), parent_action=self))
        
        self.add_action(CraftAction(entity=self.entity, recipe=self.recipe, parent_action=self))