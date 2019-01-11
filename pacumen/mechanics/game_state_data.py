from pacumen.mechanics.grid import Grid
from pacumen.mechanics.agent_state import AgentState
from pacumen.mechanics.agent_direction import Direction
from pacumen.mechanics.agent_configuration import Configuration
from pacumen.library.utilities import nearest_point


class GameStateData:
    def initialize(self, layout, num_ghost_agents):
        # TODO: Why a copy?
        # It seems that layout.dots and layout.dots.copy will be
        # providing the same thing. So why bother with a copy?
        self.dots = layout.dots.copy()

        self.pellets = layout.pellets[:]
        self.layout = layout
        self.agent_states = []
        self.score = 0
        self.score_change = 0

        number_of_ghosts = 0

        for is_pacumen, position in layout.agent_positions:
            if not is_pacumen:
                if number_of_ghosts == num_ghost_agents:
                    # Maximum number of ghosts reached.
                    continue
                else:
                    number_of_ghosts += 1

            self.agent_states.append(AgentState(Configuration(position, Direction.STOP), is_pacumen))

        self.eaten = [False for _ in self.agent_states]

    def is_a_win(self):
        self._win = True

    def is_a_loss(self):
        self._lose = True

    def get_agent_who_moved(self):
        return self._agent_moved

    def set_agent_who_moved(self, index):
        self._agent_moved = index

    def get_dot_eaten_location(self):
        return self._dot_eaten_location

    def set_dot_eaten_location(self, position):
        self._dot_eaten_location = position

    def get_pellet_eaten_location(self):
        return self._pellet_eaten_location

    def set_pellet_eaten_location(self, position):
        self._pellet_eaten_location = position

    def check_for_win(self):
        return self._win

    def check_for_loss(self):
        return self._lose

    def deep_copy(self):
        state = GameStateData(self)
        state.dots = self.dots.deep_copy()
        state.layout = self.layout.deep_copy()
        state._agent_moved = self._agent_moved
        state._dot_eaten_location = self._dot_eaten_location
        state._pellet_eaten_location = self._pellet_eaten_location
        return state

    @staticmethod
    def walls_and_dots(has_dot, has_wall):
        if has_dot:
            return '.'
        elif has_wall:
            return '%'
        else:
            return ' '

    @staticmethod
    def pacumen_display(direction):
        if direction == Direction.NORTH:
            return 'v'

        if direction == Direction.SOUTH:
            return '^'

        if direction == Direction.WEST:
            return '>'

        return '<'

    @staticmethod
    def ghost_display():
        return 'G'

    @staticmethod
    def copy_agent_states(agent_states):
        copied_states = []

        for agent_state in agent_states:
            copied_states.append(agent_state.copy())

        return copied_states

    def __init__(self, previous_state=None):
        if previous_state is not None:
            self.layout = previous_state.layout
            self.dots = previous_state.dots.shallow_copy()
            self.pellets = previous_state.pellets[:]
            self.agent_states = self.copy_agent_states(previous_state.agent_states)
            self.score = previous_state.score
            self.eaten = previous_state.eaten

        self._lose = False
        self._win = False
        self._agent_moved = None
        self._dot_eaten_location = None
        self._pellet_eaten_location = None
        self.score_change = 0

    def __str__(self):
        width, height = self.layout.width, self.layout.height
        grid_map = Grid(width, height)

        for x in range(width):
            for y in range(height):
                dots, walls = self.dots, self.layout.walls
                grid_map[x][y] = self.walls_and_dots(dots[x][y], walls[x][y])

        for x, y in self.pellets:
            grid_map[x][y] = 'o'

        for agent_state in self.agent_states:
            if agent_state is None:
                continue

            if agent_state.configuration is None:
                continue

            x, y = [int(i) for i in nearest_point(agent_state.configuration.position)]
            agent_direction = agent_state.configuration.direction

            if agent_state.is_pacumen:
                grid_map[x][y] = self.pacumen_display(agent_direction)
            else:
                grid_map[x][y] = self.ghost_display()

        return str(grid_map) + ("\nScore: %d\n" % self.score)

    def __hash__(self):
        # Get a hash of each agent state. This is just to determine if any of
        # the states cannot be hashed.
        for i, agent_state in enumerate(self.agent_states):
            try:
                int(hash(agent_state))
            except TypeError as e:
                print(e)

        return int((hash(tuple(self.agent_states)) + 13 *
                    hash(self.dots) + 113 *
                    hash(tuple(self.pellets)) + 7 *
                    hash(self.score)) % 1048575)

    def __eq__(self, other):
        if other is None:
            return False

        if not self.agent_states == other.agent_states:
            return False

        if not self.dots == other.dots:
            return False

        if not self.pellets == other.pellets:
            return False

        if not self.score == other.score:
            return False

        return True
