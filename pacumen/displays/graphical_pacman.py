import math

from pacumen.displays.graphical_builder import polygon, circle, line, square, text, move_circle, move_by, edit
from pacumen.displays.graphical_builder import wait_for_keys, change_text, change_color
from pacumen.displays.graphical_builder import create_graphic_display, stop_graphic_display, remove_from_display
from pacumen.displays.graphical_builder import refresh_display, update_display
from pacumen.displays.graphical_helpers import format_color, add, color_to_vector
from pacumen.mechanics.agent_direction import Direction


DEFAULT_GRID_SIZE = 30.0
BACKGROUND_COLOR = format_color(0, 0, 0)

WHITE = format_color(1.0, 1.0, 1.0)
BLACK = format_color(0.0, 0.0, 0.0)
RED = format_color(.9, 0, 0)
BLUE = format_color(0, .3, .9)
ORANGE = format_color(.98, .41, .07)
GREEN = format_color(.1, .75, .7)
YELLOW = format_color(1.0, 0.6, 0.0)
PURPLE = format_color(.4, 0.13, 0.91)

WALL_COLOR = format_color(0.0/255.0, 51.0/255.0, 255.0/255.0)
WALL_RADIUS = 0.15

DOT_COLOR = format_color(1, 1, 1)
DOT_SIZE = 0.1

PELLET_COLOR = format_color(1, 1, 1)
PELLET_SIZE = 0.25

PACUMEN_COLOR = format_color(255.0/255.0, 255.0/255.0, 61.0/255)
PACUMEN_OUTLINE_WIDTH = 2
PACUMEN_SCALE = 0.5

GHOST_SIZE = 0.65

GHOST_SHAPE = [
    (0, 0.3),
    (0.25, 0.75),
    (0.5, 0.3),
    (0.75, 0.75),
    (0.75, -0.5),
    (0.5, -0.75),
    (-0.5, -0.75),
    (-0.75, -0.5),
    (-0.75, 0.75),
    (-0.5, 0.3),
    (-0.25, 0.75)
]

GHOST_COLORS = [
    RED,
    BLUE,
    ORANGE,
    GREEN,
    YELLOW,
    PURPLE
]

GHOST_VEC_COLORS = map(color_to_vector, GHOST_COLORS)

SCARED_COLOR = format_color(1, 1, 1)

INFO_DISPLAY_HEIGHT = 35

SAVE_FRAMES = False
FRAMES_OUTPUT_DIR = 'frames'
FRAME_NUMBER = 0


class InfoDisplay:
    def draw_display(self):
        self.score_text = text(self.to_screen(0, 0), self.text_color, "SCORE:    0", "Times", self.font_size, "bold")

    def update_score(self, score):
        change_text(self.score_text, "SCORE: % 4d" % score)

    def to_screen(self, position, y=None):
        if y is None:
            x, y = position
        else:
            x = position

        x = self.grid_size + x
        y = self.base + y

        return x, y

    def __init__(self, layout, grid_size):
        self.grid_size = grid_size
        self.width = layout.width * grid_size
        self.height = INFO_DISPLAY_HEIGHT
        self.base = (layout.height + 1) * grid_size
        self.font_size = 24
        self.text_color = PACUMEN_COLOR
        self.score_text = None
        self.draw_display()


class PacmanDisplay:
    def initialize(self, state):
        self.distribution_images = None
        self.start_display(state)
        self.draw_static_objects(state)
        self.draw_agent_objects(state)

        # The previous state is used primarily for handling the
        # drawing of distributions.
        self.previous_state = state

    def update(self, new_state):
        agent_index = new_state.get_agent_who_moved()
        agent_state = new_state.agent_states[agent_index]

        previous_state, previous_image = self.agent_images[agent_index]

        if agent_state.is_pacumen:
            self.animate_pacumen(agent_state, previous_state, previous_image)
        else:
            self.move_ghost(agent_state, agent_index, previous_state, previous_image)

        self.agent_images[agent_index] = (agent_state, previous_image)

        if new_state.get_dot_eaten_location() is not None:
            self.remove_dot(new_state.get_dot_eaten_location(), self.dots)

        if new_state.get_pellet_eaten_location() is not None:
            self.remove_pellet(new_state.get_pellet_eaten_location(), self.pellets)

        self.info_display.update_score(new_state.score)

    def update_distributions(self, distributions):
        """
        Draws an agent's belief distributions. High posterior beliefs are
        represented by bright colors, while low beliefs are represented by
        dim colors.
        """
        distributions = map(lambda value: value.copy(), distributions)

        if self.distribution_images is None:
            self.draw_distributions(self.previous_state)

        for x in range(len(self.distribution_images)):
            for y in range(len(self.distribution_images[0])):
                image = self.distribution_images[x][y]
                weights = [dist[(x, y)] for dist in distributions]

                if sum(weights) != 0:
                    pass

                color = [0.0, 0.0, 0.0]
                colors = GHOST_VEC_COLORS[1:]

                for weight, g_color in zip(weights, colors):
                    color = [min(1.0, c + 0.95 * g * weight ** .3) for c, g in zip(color, g_color)]

                change_color(image, format_color(*color))

        refresh_display()

    def animate_pacumen(self, pacumen, previous_pacumen, image):
        if self.frame_time < 0:
            print('Press any key to step forward, "q" to play')
            keys = wait_for_keys()

            if 'q' in keys:
                self.frame_time = 0.1

        if self.frame_time > 0.01 or self.frame_time < 0:
            fx, fy = self.get_position(previous_pacumen)
            px, py = self.get_position(pacumen)
            frames = 4.0

            for i in range(1, int(frames) + 1):
                pos = px * i / frames + fx * (frames - i) / frames, py * i / frames + fy * (frames - i) / frames
                self.move_pacumen(pos, self.get_direction(pacumen), image)
                refresh_display()
                update_display(abs(self.frame_time) / frames)
        else:
            self.move_pacumen(self.get_position(pacumen), self.get_direction(pacumen), image)

        refresh_display()

    def move_pacumen(self, position, direction, image):
        screen_position = self.to_screen(position)
        endpoints = self.get_endpoints(direction, position)
        radius = PACUMEN_SCALE * self.grid_size

        move_circle(image[0], screen_position, radius, endpoints)

        refresh_display()

    def move_ghost(self, ghost, ghost_index, previous_ghost, ghost_image_parts):
        old_x, old_y = self.to_screen(self.get_position(previous_ghost))
        new_x, new_y = self.to_screen(self.get_position(ghost))
        delta = new_x - old_x, new_y - old_y

        for ghost_image_part in ghost_image_parts:
            move_by(ghost_image_part, delta)

        refresh_display()

        if ghost.scared_timer > 0:
            color = SCARED_COLOR
        else:
            color = GHOST_COLORS[ghost_index]

        edit(ghost_image_parts[0], ('fill', color), ('outline', color))
        self.move_ghost_eyes(self.get_position(ghost), self.get_direction(ghost), ghost_image_parts[-4:])

        refresh_display()

    def move_ghost_eyes(self, position, direction, eyes):
        (screen_x, screen_y) = (self.to_screen(position))
        dx = 0
        dy = 0

        if direction == 'North':
            dy = -0.2
        if direction == 'South':
            dy = 0.2
        if direction == 'East':
            dx = 0.2
        if direction == 'West':
            dx = -0.2

        move_circle(eyes[0], (screen_x + self.grid_size * GHOST_SIZE * (-0.3 + dx / 1.5),
                              screen_y - self.grid_size * GHOST_SIZE * (0.3 - dy / 1.5)),
                    self.grid_size * GHOST_SIZE * 0.2)

        move_circle(eyes[1], (screen_x + self.grid_size * GHOST_SIZE * (0.3 + dx / 1.5),
                              screen_y - self.grid_size * GHOST_SIZE * (0.3 - dy / 1.5)),
                    self.grid_size * GHOST_SIZE * 0.2)

        move_circle(eyes[2], (screen_x + self.grid_size * GHOST_SIZE * (-0.3 + dx),
                              screen_y - self.grid_size * GHOST_SIZE * (0.3 - dy)),
                    self.grid_size * GHOST_SIZE * 0.08)

        move_circle(eyes[3], (screen_x + self.grid_size * GHOST_SIZE * (0.3 + dx),
                              screen_y - self.grid_size * GHOST_SIZE * (0.3 - dy)),
                    self.grid_size * GHOST_SIZE * 0.08)

    def start_display(self, state):
        self.width = state.layout.width
        self.height = state.layout.height
        self.create_window(self.width, self.height)
        self.info_display = InfoDisplay(state.layout, self.grid_size)

    def create_window(self, width, height):
        grid_width = (width - 1) * self.grid_size
        grid_height = (height - 1) * self.grid_size
        screen_width = 2 * self.grid_size + grid_width
        screen_height = 2 * self.grid_size + grid_height + INFO_DISPLAY_HEIGHT

        create_graphic_display(screen_width, screen_height, BACKGROUND_COLOR, "Pacumen")

    def draw_distributions(self, state):
        walls = state.layout.walls
        distribution = []

        for x in range(walls.width):
            dist_x = []
            distribution.append(dist_x)

            for y in range(walls.height):
                (screen_x, screen_y) = self.to_screen((x, y))
                block = square((screen_x, screen_y), 0.5 * self.grid_size, color=BACKGROUND_COLOR, filled=1, behind=2)
                dist_x.append(block)

        self.distribution_images = distribution

    def draw_static_objects(self, state):
        self.draw_walls(state.layout.walls)
        self.dots = self.draw_dots(state.layout.dots)
        self.pellets = self.draw_pellets(state.layout.pellets)

        refresh_display()

    def draw_agent_objects(self, state):
        self.agent_images = []

        for index, agent in enumerate(state.agent_states):
            if agent.is_pacumen:
                image = self.draw_pacumen(agent)
                self.agent_images.append((agent, image))
            else:
                image = self.draw_ghost(agent, index)
                self.agent_images.append((agent, image))

        refresh_display()

    def draw_pacumen(self, pacumen):
        position = self.get_position(pacumen)
        screen_point = self.to_screen(position)
        endpoints = self.get_endpoints(self.get_direction(pacumen))

        return [circle(screen_point, PACUMEN_SCALE * self.grid_size,
                       fill_color=PACUMEN_COLOR, outline_color=PACUMEN_COLOR,
                       endpoints=endpoints, width=PACUMEN_OUTLINE_WIDTH)]

    def draw_ghost(self, ghost, ghost_index):
        position = self.get_position(ghost)
        direction = self.get_direction(ghost)
        (screen_x, screen_y) = (self.to_screen(position))
        coordinates = []

        for (x, y) in GHOST_SHAPE:
            coordinates.append((x * self.grid_size * GHOST_SIZE + screen_x,
                                y * self.grid_size * GHOST_SIZE + screen_y))

        color = self.get_ghost_color(ghost, ghost_index)
        body = polygon(coordinates, color, filled=1)

        dx = 0
        dy = 0

        if direction == 'North':
            dy = -0.2
        if direction == 'South':
            dy = 0.2
        if direction == 'East':
            dx = 0.2
        if direction == 'West':
            dx = -0.2

        left_eye = circle((screen_x + self.grid_size * GHOST_SIZE * (-0.3 + dx / 1.5),
                           screen_y - self.grid_size * GHOST_SIZE * (0.3 - dy / 1.5)),
                          self.grid_size * GHOST_SIZE * 0.2, WHITE, WHITE)

        right_eye = circle((screen_x + self.grid_size * GHOST_SIZE * (0.3 + dx / 1.5),
                            screen_y - self.grid_size * GHOST_SIZE * (0.3 - dy / 1.5)),
                           self.grid_size * GHOST_SIZE * 0.2, WHITE, WHITE)

        left_pupil = circle((screen_x + self.grid_size * GHOST_SIZE * (-0.3 + dx),
                             screen_y - self.grid_size * GHOST_SIZE * (0.3 - dy)),
                            self.grid_size * GHOST_SIZE * 0.08, BLACK, BLACK)

        right_pupil = circle((screen_x + self.grid_size * GHOST_SIZE * (0.3 + dx),
                              screen_y - self.grid_size * GHOST_SIZE * (0.3 - dy)),
                             self.grid_size * GHOST_SIZE * 0.08, BLACK, BLACK)

        ghost_image_parts = [body, left_eye, right_eye, left_pupil, right_pupil]

        return ghost_image_parts

    def draw_dots(self, dot_matrix):
        dot_images = []

        for x_num, x in enumerate(dot_matrix):
            image_row = []
            dot_images.append(image_row)

            for y_num, cell in enumerate(x):
                if cell:
                    # If there is a cell, that means there is a dot.
                    screen = self.to_screen((x_num, y_num))

                    dot = circle(screen, DOT_SIZE * self.grid_size,
                                 outline_color=DOT_COLOR, fill_color=DOT_COLOR, width=1)

                    image_row.append(dot)
                else:
                    image_row.append(None)

        return dot_images

    def draw_pellets(self, pellets):
        pellet_images = {}

        for pellet in pellets:
            (screen_x, screen_y) = self.to_screen(pellet)

            power_pellet = circle((screen_x, screen_y), PELLET_SIZE * self.grid_size,
                                  outline_color=PELLET_COLOR, fill_color=PELLET_COLOR, width=1)

            pellet_images[pellet] = power_pellet

        return pellet_images

    def draw_walls(self, wall_matrix):
        for x_num, x in enumerate(wall_matrix):
            for y_num, cell in enumerate(x):
                if cell:
                    # If there is a cell, that means there is a wall. Each
                    # quadrant of the square is drawn based on the adjacent
                    # walls.
                    position = (x_num, y_num)
                    screen = self.to_screen(position)

                    w_is_wall = self.is_wall(x_num - 1, y_num, wall_matrix)
                    e_is_wall = self.is_wall(x_num + 1, y_num, wall_matrix)
                    n_is_wall = self.is_wall(x_num, y_num + 1, wall_matrix)
                    s_is_wall = self.is_wall(x_num, y_num - 1, wall_matrix)
                    nw_is_wall = self.is_wall(x_num - 1, y_num + 1, wall_matrix)
                    sw_is_wall = self.is_wall(x_num - 1, y_num - 1, wall_matrix)
                    ne_is_wall = self.is_wall(x_num + 1, y_num + 1, wall_matrix)
                    se_is_wall = self.is_wall(x_num + 1, y_num - 1, wall_matrix)

                    # Each quadrant is a series of conditionals based on the
                    # walls. The conditionals handle drawing the following:
                    #   Inner circle
                    #   Vertical line
                    #   Horizontal line
                    #   Outer circle
                    self.draw_northeast_quadrant(screen, n_is_wall, e_is_wall, ne_is_wall)
                    self.draw_northwest_quadrant(screen, n_is_wall, w_is_wall, nw_is_wall)
                    self.draw_southeast_quadrant(screen, s_is_wall, e_is_wall, se_is_wall)
                    self.draw_southwest_quadrant(screen, s_is_wall, w_is_wall, sw_is_wall)

    def draw_northeast_quadrant(self, screen, n_is_wall, e_is_wall, ne_is_wall):
        if (not n_is_wall) and (not e_is_wall):
            circle(screen, WALL_RADIUS * self.grid_size, WALL_COLOR, WALL_COLOR, (0, 91), 'arc')

        if n_is_wall and (not e_is_wall):
            line(add(screen, (self.grid_size * WALL_RADIUS, 0)),
                 add(screen, (self.grid_size * WALL_RADIUS, self.grid_size * (-0.5) - 1)),
                 WALL_COLOR)

        if (not n_is_wall) and e_is_wall:
            line(add(screen, (0, self.grid_size * (-1) * WALL_RADIUS)),
                 add(screen, (self.grid_size * 0.5 + 1, self.grid_size * (-1) * WALL_RADIUS)),
                 WALL_COLOR)

        if n_is_wall and e_is_wall and (not ne_is_wall):
            circle(add(screen, (self.grid_size * 2 * WALL_RADIUS, self.grid_size * (-2) * WALL_RADIUS)),
                   WALL_RADIUS * self.grid_size - 1, WALL_COLOR, WALL_COLOR, (180, 271), 'arc')

            line(add(screen, (self.grid_size * 2 * WALL_RADIUS - 1, self.grid_size * (-1) * WALL_RADIUS)),
                 add(screen, (self.grid_size * 0.5 + 1, self.grid_size * (-1) * WALL_RADIUS)),
                 WALL_COLOR)

            line(add(screen, (self.grid_size * WALL_RADIUS, self.grid_size * (-2) * WALL_RADIUS + 1)),
                 add(screen, (self.grid_size * WALL_RADIUS, self.grid_size * (-0.5))),
                 WALL_COLOR)

    def draw_northwest_quadrant(self, screen, n_is_wall, w_is_wall, nw_is_wall):
        if (not n_is_wall) and (not w_is_wall):
            circle(screen, WALL_RADIUS * self.grid_size, WALL_COLOR, WALL_COLOR, (90, 181), 'arc')

        if n_is_wall and (not w_is_wall):
            line(add(screen, (self.grid_size * (-1) * WALL_RADIUS, 0)),
                 add(screen, (self.grid_size * (-1) * WALL_RADIUS, self.grid_size * (-0.5) - 1)),
                 WALL_COLOR)

        if (not n_is_wall) and w_is_wall:
            line(add(screen, (0, self.grid_size * (-1) * WALL_RADIUS)),
                 add(screen, (self.grid_size * (-0.5) - 1, self.grid_size * (-1) * WALL_RADIUS)),
                 WALL_COLOR)

        if n_is_wall and w_is_wall and (not nw_is_wall):
            circle(add(screen, (self.grid_size * (-2) * WALL_RADIUS, self.grid_size * (-2) * WALL_RADIUS)),
                   WALL_RADIUS * self.grid_size-1, WALL_COLOR, WALL_COLOR, (270, 361), 'arc')

            line(add(screen, (self.grid_size * (-2) * WALL_RADIUS + 1, self.grid_size * (-1) * WALL_RADIUS)),
                 add(screen, (self.grid_size * (-0.5), self.grid_size * (-1) * WALL_RADIUS)),
                 WALL_COLOR)

            line(add(screen, (self.grid_size * (-1) * WALL_RADIUS, self.grid_size * (-2) * WALL_RADIUS+1)),
                 add(screen, (self.grid_size * (-1) * WALL_RADIUS, self.grid_size * (-0.5))),
                 WALL_COLOR)

    def draw_southeast_quadrant(self, screen, s_is_wall, e_is_wall, se_is_wall):
        if (not s_is_wall) and (not e_is_wall):
            circle(screen, WALL_RADIUS * self.grid_size, WALL_COLOR, WALL_COLOR, (270, 361), 'arc')

        if s_is_wall and (not e_is_wall):
            line(add(screen, (self.grid_size * WALL_RADIUS, 0)),
                 add(screen, (self.grid_size * WALL_RADIUS, self.grid_size * 0.5 + 1)),
                 WALL_COLOR)

        if (not s_is_wall) and e_is_wall:
            line(add(screen, (0, self.grid_size * 1 * WALL_RADIUS)),
                 add(screen, (self.grid_size * 0.5 + 1, self.grid_size * 1 * WALL_RADIUS)),
                 WALL_COLOR)

        if s_is_wall and e_is_wall and (not se_is_wall):
            circle(add(screen, (self.grid_size * 2 * WALL_RADIUS, self.grid_size * 2 * WALL_RADIUS)),
                   WALL_RADIUS * self.grid_size - 1, WALL_COLOR, WALL_COLOR, (90, 181), 'arc')

            line(add(screen, (self.grid_size * 2 * WALL_RADIUS - 1, self.grid_size * 1 * WALL_RADIUS)),
                 add(screen, (self.grid_size * 0.5, self.grid_size * 1 * WALL_RADIUS)),
                 WALL_COLOR)

            line(add(screen, (self.grid_size * WALL_RADIUS, self.grid_size * 2 * WALL_RADIUS - 1)),
                 add(screen, (self.grid_size * WALL_RADIUS, self.grid_size * 0.5)),
                 WALL_COLOR)

    def draw_southwest_quadrant(self, screen, s_is_wall, w_is_wall, sw_is_wall):
        if (not s_is_wall) and (not w_is_wall):
            circle(screen, WALL_RADIUS * self.grid_size, WALL_COLOR, WALL_COLOR, (180, 271), 'arc')

        if s_is_wall and (not w_is_wall):
            line(add(screen, (self.grid_size * (-1) * WALL_RADIUS, 0)),
                 add(screen, (self.grid_size * (-1) * WALL_RADIUS, self.grid_size * 0.5 + 1)),
                 WALL_COLOR)

        if (not s_is_wall) and w_is_wall:
            line(add(screen, (0, self.grid_size * 1 * WALL_RADIUS)),
                 add(screen, (self.grid_size * (-0.5) - 1, self.grid_size * 1 * WALL_RADIUS)),
                 WALL_COLOR)

        if s_is_wall and w_is_wall and (not sw_is_wall):
            circle(add(screen, (self.grid_size * (-2) * WALL_RADIUS, self.grid_size * 2 * WALL_RADIUS)),
                   WALL_RADIUS * self.grid_size - 1, WALL_COLOR, WALL_COLOR, (0, 91), 'arc')

            line(add(screen, (self.grid_size * (-2) * WALL_RADIUS + 1, self.grid_size * 1 * WALL_RADIUS)),
                 add(screen, (self.grid_size * (-0.5), self.grid_size * 1 * WALL_RADIUS)),
                 WALL_COLOR)

            line(add(screen, (self.grid_size * (-1) * WALL_RADIUS, self.grid_size * 2 * WALL_RADIUS - 1)),
                 add(screen, (self.grid_size * (-1) * WALL_RADIUS, self.grid_size * 0.5)),
                 WALL_COLOR)

    def draw_expanded_cells(self, cells):
        """
        Draws an overlay of expanded grid positions. This is specifically for
        search agents, where it is desirable to see how the nodes of a given
        maze were expanded.
        """
        n = float(len(cells))
        base_color = [1.0, 0.0, 0.0]

        self.clear_expanded_cells()
        self.expanded_cells = []

        for k, cell in enumerate(cells):
            screen_pos = self.to_screen(cell)
            cell_color = format_color(*[(n - k) * c * .5 / n + .25 for c in base_color])
            block = square(screen_pos, 0.5 * self.grid_size, color=cell_color, filled=1, behind=2)
            self.expanded_cells.append(block)

            if self.frame_time < 0:
                refresh_display()

    def clear_expanded_cells(self):
        if 'expanded_cells' in dir(self) and len(self.expanded_cells) > 0:
            for cell in self.expanded_cells:
                remove_from_display(cell)

    def to_screen(self, point):
        (x, y) = point
        x = (x + 1) * self.grid_size
        y = (self.height - y) * self.grid_size
        return x, y

    @staticmethod
    def finish():
        stop_graphic_display()

    @staticmethod
    def remove_dot(cell, dot_images):
        x, y = cell
        remove_from_display(dot_images[x][y])

    @staticmethod
    def remove_pellet(cell, pellet_images):
        x, y = cell
        remove_from_display(pellet_images[(x, y)])

    @staticmethod
    def get_position(agent_state):
        if agent_state.configuration is None:
            return -1000, -1000

        return agent_state.configuration.get_position()

    @staticmethod
    def get_direction(agent_state):
        if agent_state.configuration is None:
            return Direction.STOP

        return agent_state.configuration.get_direction()

    @staticmethod
    def get_ghost_color(ghost, ghost_index):
        if ghost.scared_timer > 0:
            return SCARED_COLOR
        else:
            return GHOST_COLORS[ghost_index]

    @staticmethod
    def get_endpoints(direction, position=(0, 0)):
        x, y = position
        pos = x - int(x) + y - int(y)
        width = 30 + 80 * math.sin(math.pi * pos)
        delta = width / 2

        if direction == 'West':
            endpoints = (180 + delta, 180 - delta)
        elif direction == 'North':
            endpoints = (90 + delta, 90 - delta)
        elif direction == 'South':
            endpoints = (270 + delta, 270 - delta)
        else:
            endpoints = (0 + delta, 0 - delta)

        return endpoints

    @staticmethod
    def is_wall(x, y, walls):
        if x < 0 or y < 0:
            return False

        if x >= walls.width or y >= walls.height:
            return False

        return walls[x][y]

    def __init__(self, zoom=1.0, frame_time=0.0):
        self.zoom = zoom
        self.frame_time = frame_time
        self.grid_size = DEFAULT_GRID_SIZE * zoom
        self.agent_images = []
        self.expanded_cells = []
        self.distribution_images = None
        self.info_display = None
        self.previous_state = None
        self.width = None
        self.height = None
        self.dots = None
        self.pellets = None


def save_display_frames():
    import os

    global SAVE_FRAMES, FRAME_NUMBER, FRAMES_OUTPUT_DIR

    if not SAVE_FRAMES:
        return

    if not os.path.exists(FRAMES_OUTPUT_DIR):
        os.mkdir(FRAMES_OUTPUT_DIR)

    name = os.path.join(FRAMES_OUTPUT_DIR, 'frame_%08d.ps' % FRAME_NUMBER)
    FRAME_NUMBER += 1

    from pacumen.displays.graphical_builder import save_display
    save_display(name)


def test():
    from pacumen.mechanics import layout
    board = layout.get_layout("testing")

    from pacumen.mechanics import game_state
    init_state = game_state.GameState()

    init_state.initialize(board)

    display = PacmanDisplay()
    display.initialize(init_state.data)

    from pacumen.displays.graphical_builder import show_display
    show_display()
