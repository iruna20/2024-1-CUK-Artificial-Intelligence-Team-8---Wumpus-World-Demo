from pickle import FALSE, TRUE
import random
import copy
import enum
import printGUI as gui


class Orientation(enum.Enum):
    north = 1
    south = 2
    east = 3
    west = 4

    @property
    def turn_left(self):
        dict_turn_left = {
            Orientation.north: Orientation.west,
            Orientation.south: Orientation.east,
            Orientation.east: Orientation.north,
            Orientation.west: Orientation.south
        }
        new_orientation = dict_turn_left.get(self)
        return new_orientation

    @property
    def turn_right(self):
        dict_turn_right = {
            Orientation.north: Orientation.east,
            Orientation.south: Orientation.west,
            Orientation.east: Orientation.south,
            Orientation.west: Orientation.north
        }
        new_orientation = dict_turn_right.get(self)
        return new_orientation


class Action():
    def __init__(self, is_forward=False, is_turn_left=False, is_turn_right=False,
                 is_shoot=False, is_grab=False, is_climb=False):
        assert is_forward ^ is_turn_left ^ is_turn_right ^ is_shoot ^ is_grab ^ is_climb
        self.is_forward = is_forward
        self.is_turn_left = is_turn_left
        self.is_turn_right = is_turn_right
        self.is_shoot = is_shoot
        self.is_grab = is_grab
        self.is_climb = is_climb

    @classmethod
    def forward(cls):
        return Action(is_forward=True)

    @classmethod
    def turn_left(cls):
        return Action(is_turn_left=True)

    @classmethod
    def turn_right(cls):
        return Action(is_turn_right=True)

    @classmethod
    def shoot(cls):
        return Action(is_shoot=True)

    @classmethod
    def grab(cls):
        return Action(is_grab=True)

    @classmethod
    def climb(cls):
        return Action(is_climb=True)

    def get(self):
        if self.is_forward:
            action_str = "forward"
        elif self.is_turn_left:
            action_str = "turn_left"
        elif self.is_turn_right:
            action_str = "turn_right"
        elif self.is_shoot:
            action_str = "shoot"
        elif self.is_grab:
            action_str = "grab"
        else:
            action_str = "climb"
        return action_str


from collections import namedtuple


class Coords(namedtuple('Coords', 'x y')):
    pass


class Percept():
    def __init__(self, stench, breeze, glitter, bump, scream, is_terminated, reward):
        self.stench = stench
        self.breeze = breeze
        self.glitter = glitter
        self.bump = bump
        self.scream = scream
        self.is_terminated = is_terminated
        self.reward = reward

    def show(self):
        print("stench: {}, breeze: {}, glitter: {}, bump: {}, scream: {}, is_terminated: {}, reward: {}"
              .format(self.stench, self.breeze, self.glitter, self.bump, self.scream, self.is_terminated, self.reward))
        
    def toDictionary(self):
        value = {
            'Stench': self.stench,
            'Breeze': self.breeze,
            'Glitter': self.glitter,
            'Bump': self.bump,
            'Scream': self.scream,
            'Terminated': self.is_terminated,
            'Reward': self.reward
        }
        return value


def random_location_except_origin(grid_width, grid_height, existing_locations):
    locations = []
    for col in range(grid_width):
        for row in range(grid_height):
            cell = Coords(x=col, y=row)
            if cell != Coords(0, 0) and cell not in existing_locations:
                locations.append(cell)
    return random.choice(locations)


def create_pit_locations(grid_width, grid_height):
    locations = set()
    while len(locations) < 1 or (len(locations) < 2 and random.random() < 0.1):
        locations.add(random_location_except_origin(grid_width, grid_height, locations))
    return list(locations)


class AgentState():
    def __init__(self, location=Coords(0, 0), orientation=Orientation.east, has_gold=False, arrow_cnt=3,
                 is_alive=True):
        self.location = location
        self.orientation = orientation
        self.has_gold = has_gold
        self.arrow_cnt = arrow_cnt
        self.is_alive = is_alive

    def turn_left(self):
        new_state = copy.deepcopy(self)
        new_state.orientation = new_state.orientation.turn_left
        return new_state

    def turn_right(self):
        new_state = copy.deepcopy(self)
        new_state.orientation = new_state.orientation.turn_right
        return new_state

    def forward(self, grid_width, grid_height):
        if self.orientation == Orientation.north:
            new_loc = Coords(self.location.x, min(grid_height - 1, self.location.y + 1))
        elif self.orientation == Orientation.south:
            new_loc = Coords(self.location.x, max(0, self.location.y - 1))
        elif self.orientation == Orientation.east:
            new_loc = Coords(min(grid_width - 1, self.location.x + 1), self.location.y)
        else:
            new_loc = Coords(max(0, self.location.x - 1), self.location.y)  # if Orientation.west
        new_state = copy.deepcopy(self)
        new_state.location = new_loc
        return new_state


class Environment():
    def __init__(self, grid_width, grid_height, allow_climb_without_gold, agent, pit_locations,
                 terminated, wumpus_loc, wumpus_alive, gold_loc):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.allow_climb_without_gold = allow_climb_without_gold
        self.agent = agent
        self.pit_locations = pit_locations
        self.terminated = terminated
        self.wumpus_loc = wumpus_loc
        self.wumpus_alive = wumpus_alive
        self.gold_loc = gold_loc

    def is_pit_at(self, coords):
        return coords in self.pit_locations

    def is_wumpus_at(self, coords):
        return coords == self.wumpus_loc

    def is_agent_at(self, coords):
        return coords == self.agent.location

    def is_gold_at(self, coords):
        return coords == self.gold_loc

    def wumpus_in_line_of_fire(self):
        if self.agent.orientation == Orientation.west:
            return self.agent.location.x > self.wumpus_loc.x and self.agent.location.y == self.wumpus_loc.y
        if self.agent.orientation == Orientation.east:
            return self.agent.location.x < self.wumpus_loc.x and self.agent.location.y == self.wumpus_loc.y
        if self.agent.orientation == Orientation.south:
            return self.agent.location.x == self.wumpus_loc.x and self.agent.location.y > self.wumpus_loc.y
        if self.agent.orientation == Orientation.north:
            return self.agent.location.x == self.wumpus_loc.x and self.agent.location.y < self.wumpus_loc.y

    def kill_attempt_successful(self):
        return self.agent.arrow_cnt > 0 and self.wumpus_alive and self.wumpus_in_line_of_fire()

    def adjacent_cells(self, coords=Coords(0, 0)):
        return [
            Coords(coords.x - 1, coords.y) if coords.x > 0 else None,  # to the left
            Coords(coords.x + 1, coords.y) if coords.x < (self.grid_width - 1) else None,  # to the right
            Coords(coords.x, coords.y - 1) if coords.y > 0 else None,  # below
            Coords(coords.x, coords.y + 1) if coords.y < (self.grid_height - 1) else None,  # above
        ]

    def is_pit_adjacent(self, coords):
        for cell in self.adjacent_cells(coords):
            if cell is None:
                continue
            if cell in self.pit_locations:
                return True
        return False

    def is_wumpus_adjacent(self, coords):
        for cell in self.adjacent_cells(coords):
            if cell is None:
                continue
            if self.is_wumpus_at(cell):
                return True
        return False

    #def is_gold_adjacent(self, coords):
    #    adjacent_cells = self.adjacent_cells(coords)
    #    for cell in adjacent_cells:
    #        if cell and self.is_gold_at(cell):
    #            return True
    #    return False
    
    def is_breeze(self):
        return self.is_pit_adjacent(self.agent.location)

    def is_stench(self):
        return self.is_wumpus_adjacent(self.agent.location) or self.is_wumpus_at(self.agent.location)

    def is_glitter(self):
        return self.is_gold_at(self.agent.location)
        #return self.is_gold_adjacent(self.agent.location) or self.is_gold_at(self.agent.location)

    def apply_action(self, action):
        if self.terminated:
            return (self, Percept(False, False, False, False, False, True, 0))
        else:
            if action.is_forward:
                moved_agent = self.agent.forward(self.grid_width, self.grid_height)
                death = (self.is_wumpus_at(moved_agent.location) and self.wumpus_alive) or self.is_pit_at(
                    moved_agent.location)
                new_agent = copy.deepcopy(moved_agent)
                new_agent.is_alive = not death
                new_gold_loc = new_agent.location if self.agent.has_gold else self.gold_loc
                new_env = Environment(self.grid_width, self.grid_height, self.allow_climb_without_gold,
                                      new_agent, self.pit_locations, death, self.wumpus_loc, self.wumpus_alive,
                                      new_gold_loc)
                percept = Percept(new_env.is_stench(), new_env.is_breeze(), new_env.is_glitter(),
                                  new_agent.location == self.agent.location, False, death,
                                  -1 if new_agent.is_alive else -1001)
                return (new_env, percept)

            if action.is_turn_left:
                new_env = Environment(self.grid_width, self.grid_height, self.allow_climb_without_gold,
                                      self.agent.turn_left(), self.pit_locations, self.terminated, self.wumpus_loc,
                                      self.wumpus_alive, self.gold_loc)
                percept = Percept(self.is_stench(), self.is_breeze(), self.is_glitter(), False, False, False, -1)
                return (new_env, percept)

            if action.is_turn_right:
                new_env = Environment(self.grid_width, self.grid_height, self.allow_climb_without_gold,
                                      self.agent.turn_right(), self.pit_locations, self.terminated, self.wumpus_loc,
                                      self.wumpus_alive, self.gold_loc)
                percept = Percept(self.is_stench(), self.is_breeze(), self.is_glitter(), False, False, False, -1)
                return (new_env, percept)

            if action.is_grab:
                new_agent = copy.deepcopy(self.agent)
                new_agent.has_gold = self.is_gold_at(new_agent.location)
                new_gold_loc = new_agent.location if new_agent.has_gold else self.gold_loc
                new_env = Environment(self.grid_width, self.grid_height, self.allow_climb_without_gold,
                                      new_agent, self.pit_locations, self.terminated, self.wumpus_loc,
                                      self.wumpus_alive,
                                      new_gold_loc)
                percept = Percept(self.is_stench(), self.is_breeze(), self.is_glitter(), False, False, False, -1)
                return (new_env, percept)

            if action.is_climb:
                in_start_loc = self.agent.location == Coords(0, 0)
                success = self.agent.has_gold and in_start_loc
                is_terminated = success or (self.allow_climb_without_gold and in_start_loc)
                new_env = Environment(self.grid_width, self.grid_height, self.allow_climb_without_gold,
                                      self.agent, self.pit_locations, is_terminated, self.wumpus_loc, self.wumpus_alive,
                                      self.gold_loc)
                percept = Percept(self.is_stench(), self.is_breeze(), self.is_glitter(), False, False, is_terminated,
                                  999 if success else -1)
                return (new_env, percept)

            if action.is_shoot:
                before_arrow_cnt = self.agent.arrow_cnt
                wumpus_killed = self.kill_attempt_successful()
                new_agent = copy.deepcopy(self.agent)
                new_agent.arrow_cnt -= 1
                new_env = Environment(self.grid_width, self.grid_height, self.allow_climb_without_gold,
                                      new_agent, self.pit_locations, self.terminated, self.wumpus_loc,
                                      self.wumpus_alive and (not wumpus_killed), self.gold_loc)
                percept = Percept(self.is_stench(), self.is_breeze(), self.is_glitter(), False, wumpus_killed, False,
                                  -11 if before_arrow_cnt > 0 else -1)
                return (new_env, percept)

    @classmethod
    def new_game(cls, grid_width, grid_height, allow_climb_without_gold):
        new_pit_locations = create_pit_locations(grid_width, grid_height)
        new_wumpus_loc = random_location_except_origin(grid_width, grid_height, new_pit_locations)
        new_gold_loc = random_location_except_origin(grid_width, grid_height, new_pit_locations + [new_wumpus_loc])
        env = Environment(grid_width, grid_height, allow_climb_without_gold,
                          AgentState(), new_pit_locations, False, new_wumpus_loc, True, new_gold_loc)
        percept = Percept(env.is_stench(), env.is_breeze(), env.is_glitter(), False, False, False, 0.0)
        return (env, percept)

    def visualize(self):
        grid = [[() for _ in range(self.grid_width)] for _ in range(self.grid_height)]

        for y in range(self.grid_height):
            for x in range(self.grid_width):
                result = grid[y][x]
                if self.is_agent_at(Coords(x, y)):
                    str_agent = "Agent_" + (str)(self.agent.orientation.value)
                    result = (*result, str_agent)
                if self.is_pit_at(Coords(x, y)):
                    result = (*result, "Pit")
                if self.is_gold_at(Coords(x, y)):
                    result = (*result, "Gold")
                if self.is_wumpus_at(Coords(x, y)):
                    wumpus_symbol = "Wumpus" if self.wumpus_alive else "DeadWumpus"
                    result = (*result, wumpus_symbol)
                if self.is_pit_adjacent(Coords(x, y)):
                    result = (*result, "Breeze")
                if self.is_wumpus_adjacent(Coords(x, y)):
                    result = (*result, "Stench")
                if self.is_gold_at(Coords(x, y)): #self.is_gold_adjacent(Coords(x, y)):
                    result = (*result, "Glitter")
                grid[y][x] = result

        for row in reversed(grid):
            row_str_list = []
            for col in row:
                col_str = "Empty"
                for i in range(0, len(col)):
                    e = col[i]
                    if (col_str != "Empty"):
                        col_str += "," + e
                    else :
                        col_str = e
                row_str_list.append(col_str)
            print("|".join(row_str_list))
        return grid


class Agent:
    def __init__(self):
        pass

    def select_action(self, percept):
        raise NotImplementedError()


class NaiveAgent(Agent):
    def select_action(self, percept):
        actions = [Action.forward(), Action.turn_left(), Action.turn_right(), Action.shoot(), Action.grab(),
                   Action.climb()]
        # actions = [Action.forward(), Action.turn_left(), Action.turn_right(), Action.shoot()] 테스트용
        next_action = random.choice(actions)
        return next_action

"""
class ReflexAgent(Agent):
    def __init__(self):
        self.has_gold = False
        self.has_arrow = True
        self.orientation = Orientation.east
        self.location = Coords(0, 0)
        self.previous_action = None

    def update_state(self, percept, action):
        if action.is_grab and percept.glitter and self.is_gold_at(self.location):
            self.has_gold = True
        if action.is_shoot:
            self.has_arrow = False
        if action.is_turn_left:
            self.orientation = self.orientation.turn_left
        if action.is_turn_right:
            self.orientation = self.orientation.turn_right
        if action.is_forward and not percept.bump:
            if self.orientation == Orientation.north:
                self.location = Coords(self.location.x, self.location.y + 1)
            elif self.orientation == Orientation.south:
                self.location = Coords(self.location.x, self.location.y - 1)
            elif self.orientation == Orientation.east:
                self.location = Coords(self.location.x + 1, self.location.y)
            elif self.orientation == Orientation.west:
                self.location = Coords(self.location.x - 1, self.location.y)

    def select_action(self, percept):
        # 귀환 조건 확인
        if self.has_gold and self.location == Coords(0, 0):
            return Action.climb()

        # 행동 선택
        if percept.glitter and not self.has_gold:
            action = Action.grab()
        elif percept.stench and self.has_arrow:
            action = Action.shoot()
        elif percept.bump:
            action = random.choice([Action.turn_left(), Action.turn_right()])
        elif percept.breeze:
            if self.previous_action in [Action.turn_left(), Action.turn_right()]:
                action = Action.forward()
            else:
                action = random.choice([Action.turn_left(), Action.turn_right(), Action.forward()])
        else:
            action = Action.forward()

        # 상태 업데이트
        self.update_state(percept, action)
        self.previous_action = action
        return action
"""

class ReflexAgent(Agent):
    def __init__(self):
        self.accepted_locations = set([Coords(0, 0)])   # 확실히 안전하여 이동이 허용된 위치
        self.visited_locations = set([Coords(0, 0)])  # 방문한 위치
        self.gold_possible_locations = set()  # Gold가 있을 수 있는 위치
        self.bumped_locations = set()   # Bump가 발생한 위치
        self.wumpus_possible_locations = set()  # Wumpus가 있을 수 있는 위치
        self.pit_possible_locations = set()  # 구덩이가 있을 수 있는 위치
        self.arrow_cnt = 3  # 화살 갯수
        self.percept = None

    def choice_default_action(self):
        return random.choice([Action.turn_left(), Action.turn_right(), Action.forward()])

    def select_action(self, env, percept):
        self.percept = percept

        self.update_kb(env)  # 위치 정보 업데이트
        
        # 금을 가지고 있다면
        if env.agent.has_gold:
            if env.agent.location == Coords(0, 0):  # 시작 위치에 도달하면 climb
                return Action.climb()
            else:   # 아니라면
                return self.go_destination(env, Coords(0, 0)) # 시작 위치를 향해 이동
        else:    # 금이 없다면
            if percept.glitter: # glitter가 발생 시 금을 잡기 위해 시도
                action = self.move_and_grab_gold(env)
                if action == Action.grab():
                    env.agent.has_gold = True
                if action:
                    return action
            else:   # 발생하지 않았고 gold 후보 위치가 있다면 그곳으로 이동
                glitter_action = self.move_to_gold_possible_location(env)
                if glitter_action:
                    return glitter_action
            
        # 부딪히면 기록 후 주변 4방향 중 안전한 위치로 이동
        if percept.bump:
            self.update_bumped_location(env)
            safe_action = self.move_to_safe_location(env)
            if safe_action:
                return safe_action

        # stench가 발생하고 Wumpus가 살아있고 화살이 있으면 Shoot
        if percept.stench and env.wumpus_alive and self.arrow_cnt > 0:
            action = self.shoot_wumpus_cheat(env)
            if action == Action.shoot():
                self.arrow_cnt -= 1
            return action
        
        
        # 가보지 않은 안전한 위치가 있다면 그곳으로 이동
        safe_action = self.move_to_safe_location(env)
        if safe_action:
            return safe_action

        # 기본 동작 선택
        return self.choice_default_action()

    # 바라보고 있는 위치를 반환
    def get_look_location(self, env):
        if env.agent.orientation == Orientation.north:
            return Coords(env.agent.location.x, env.agent.location.y + 1)
        elif env.agent.orientation == Orientation.south:
            return Coords(env.agent.location.x, env.agent.location.y - 1)
        elif env.agent.orientation == Orientation.east:
            return Coords(env.agent.location.x - 1, env.agent.location.y)
        elif env.agent.orientation == Orientation.west:
            return Coords(env.agent.location.x + 1, env.agent.location.y)
        
    def update_bumped_location(self, env):
        self.bumped_locations.add(self.get_look_location(env))
    
    def go_destination(self, env, destination):
        path = self.find_safe_path(env, destination)
        path_str = ''.join(str(s) for s in path)
        #print("PATH : " + path_str)
        for next_location in path:
            if next_location:
                #print("LET'S GO TO : {}, {}".format(next_location.x, next_location.y))
                return self.move_towards_location(env, next_location)
        return self.choice_default_action()

    # gold가 있다면 grab, 없다면 gold 후보 위치 기록 후 안전한 gold 후보 위치로 이동
    def move_and_grab_gold(self, env):
        if env.is_gold_at(env.agent.location):
            return Action.grab()
        for coords in env.adjacent_cells(env.agent.location):
            if coords is not None:
                self.gold_possible_locations.add(coords)
        self.gold_possible_locations = (self.gold_possible_locations - self.visited_locations)
        return self.move_to_gold_possible_location(env)

    # 가까운 gold 후보 위치로 이동
    def move_to_gold_possible_location(self, env):
        safe_and_gold_possible_locations = (self.get_safe_and_unknown_locations(env) & self.gold_possible_locations)
        if len(safe_and_gold_possible_locations) != 0:
            location = min(safe_and_gold_possible_locations,
                                        key=lambda loc: self.manhattan_distance(env.agent.location, loc))
            if location:
                locations_str = ''.join(str(s) for s in safe_and_gold_possible_locations)
                print("Gold Possible Locations : " + locations_str)
                print(location)
                return self.go_destination(env, location)
        return None

    def update_kb(self, env):
        self.gold_possible_locations.discard(env.agent.location)
        self.visited_locations.add(env.agent.location)
        self.accepted_locations.add(env.agent.location)
        
        is_currnet_safe = ((not env.wumpus_alive) or (not self.percept.stench)) and not self.percept.breeze
        if is_currnet_safe:
            for coords in env.adjacent_cells(env.agent.location):
                if coords is not None:
                    self.accepted_locations.add(coords)
                    
        if not env.wumpus_alive:
            self.update_wumpus_possible_locations(env, True)
        elif self.percept.stench:
            self.update_wumpus_possible_locations(env, not env.wumpus_alive)
            
        if self.percept.breeze:
            self.update_pit_possible_locations(env)

    def update_wumpus_possible_locations(self, env, reset=False):
        if(reset):
            self.wumpus_possible_locations.clear()
            return
        for coords in env.adjacent_cells(env.agent.location):
            if coords is not None:
                self.wumpus_possible_locations.add(coords)
        self.wumpus_possible_locations = self.wumpus_possible_locations - self.accepted_locations

    def update_pit_possible_locations(self, env):
        for coords in env.adjacent_cells(env.agent.location):
            if coords is not None:
                self.pit_possible_locations.add(coords)
        self.pit_possible_locations = self.pit_possible_locations - self.accepted_locations

    def shoot_wumpus_cheat(self, env):
        # Wumpus가 있는 방향으로 쏘는 로직 (agent가 env를 직접 참고하기에 규칙 위반)
        if env.agent.orientation == Orientation.north:
            if any(env.is_wumpus_at(Coords(env.agent.location.x, y)) for y in range(env.agent.location.y + 1, env.grid_height)):
                return Action.shoot()
        elif env.agent.orientation == Orientation.south:
            if any(env.is_wumpus_at(Coords(env.agent.location.x, y)) for y in range(0, env.agent.location.y)):
                return Action.shoot()
        elif env.agent.orientation == Orientation.east:
            if any(env.is_wumpus_at(Coords(x, env.agent.location.y)) for x in range(env.agent.location.x + 1, env.grid_width)):
                return Action.shoot()
        elif env.agent.orientation == Orientation.west:
            if any(env.is_wumpus_at(Coords(x, env.agent.location.y)) for x in range(0, env.agent.location.x)):
                return Action.shoot()
        return self.move_to_safe_location(env)
    
    def shoot_wumpus(self, env):
        return Action.shoot()

    def move_to_safe_location(self, env, target_location=None):
        safe_locations = self.get_safe_and_unknown_locations(env)
        #safe_locations_str = ''.join(str(s) for s in safe_locations)
        #ac_lo_str = ''.join(str(s) for s in self.accepted_locations)
        #print("Safe Locations : " + safe_locations_str)
        #print("Accepted Locations : " + ac_lo_str)
        if safe_locations:
            # 목적지가 주어지면 목적지로 이동
            if target_location:
                return self.go_destination(env, target_location)

            # 그렇지 않은 경우 안전하고 가보지 않은 가까운 위치로 이동
            destination = min(safe_locations,
                                        key=lambda loc: self.manhattan_distance(env.agent.location, loc))
            return self.go_destination(env, destination)
        return self.choice_default_action()

    def get_safe_and_unknown_locations(self, env):
        #safe_locations = set()
        #for x in range(env.grid_width):
        #    for y in range(env.grid_height):
        #        safe_locations.add(Coords(x, y))
        locations = self.accepted_locations
        locations = (locations - self.pit_possible_locations)
        locations = (locations - self.bumped_locations)
        if(env.wumpus_alive):
            locations = (locations - self.wumpus_possible_locations)
        locations = (locations - self.visited_locations)
        return locations

    def move_towards_location(self, env, target_location):
        #print("TargetLocation : {}, {}".format(target_location.x, target_location.y))
                
        dx = target_location.x - env.agent.location.x
        dy = target_location.y - env.agent.location.y

        if abs(dx) > abs(dy):
            if dx > 0:
                if env.agent.orientation != Orientation.east:
                    return self.turn_towards(env, Orientation.east)
                else:
                    return Action.forward()
            elif dx < 0:
                if env.agent.orientation != Orientation.west:
                    return self.turn_towards(env, Orientation.west)
                else:
                    return Action.forward()
        else:
            if dy > 0:
                if env.agent.orientation != Orientation.north:
                    return self.turn_towards(env, Orientation.north)
                else:
                    return Action.forward()
            elif dy < 0:
                if env.agent.orientation != Orientation.south:
                    return self.turn_towards(env, Orientation.south)
                else:
                    return Action.forward()
        return None

    def find_safe_path(self, env, target_location):
        queue = [(env.agent.location, [])]
        visited = set()

        while queue:
            current_location, path = queue.pop(0)
            if current_location == target_location:
                return path + [target_location]

            if current_location in visited:
                continue

            visited.add(current_location)

            #print("CURRENT : {}, {}".format(current_location.x, current_location.y))
            
            locations = (set(env.adjacent_cells(current_location)) & self.accepted_locations) - self.wumpus_possible_locations - self.pit_possible_locations
            #lo_str = ''.join(str(s) for s in locations)
            #print("NEIGHBOR and ACCEPTED : " + lo_str)
            
            for neighbor in locations:
                # 인접한 위치가 유효하고 방문하지 않았으며 위험 위치가 아닌 경우 큐에 추가
                if neighbor and neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))
                    #print("NEIGHBOR : {}, {}".format(neighbor.x, neighbor.y))

        return []

    def turn_towards(self, env, target_orientation):
        if target_orientation == env.agent.orientation.turn_left:
            return Action.turn_left()
        else:
            return Action.turn_right()

    def manhattan_distance(self, loc1, loc2):
        return abs(loc1.x - loc2.x) + abs(loc1.y - loc2.y)

def main():
    gui.reset_directory()
    
    # 초기 상태 설정
    agent = ReflexAgent()
    (env, percept) = Environment.new_game(4, 4, True)
    c = 0
    grid = env.visualize()
    total_reward = 0
    current_action_str = "inital state"
    
    # Headless 여부 (False일 경우 GUI 출력됨)
    is_headless = False
    
    # 이미지 출력 및 행동 반복
    while not percept.is_terminated:
        # 다음 행동을 정하고, 이전 행동과 다음 행동을 포함한 이미지 저장
        next_action = agent.select_action(env, percept)
        gui.save_img(c, grid, current_action_str, next_action.get(), percept.toDictionary(), is_headless)
        c += 1
        
        percept.show()
        print("Action: " + next_action.get())  # print action
        total_reward += percept.reward
        
        # 액션 실행 후 환경 변경
        (env, percept) = env.apply_action(next_action)
        grid = env.visualize()
        current_action_str = next_action.get()
    total_reward = percept.reward
    gui.save_img(c, grid, current_action_str, "-", percept.toDictionary(), is_headless)
    percept.show()
    print("Action: " + next_action.get())  # print action
        
    print("Total reward:", total_reward)


if __name__ == '__main__':
    main()

