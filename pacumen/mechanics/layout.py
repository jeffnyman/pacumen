import os
import random
import logging

from pacumen.mechanics.grid import Grid
from pacumen.library.utilities import manhattan_distance


class Layout:
    """
    A Layout manages the static information about the environment. Each
    layout is made of a series of characters. Each character represents
    a different type of object. The character breakdown is:

    % - Wall
    . - Food
    o - Capsule
    G - Ghost agent
    P - Pacumen agent

    It is possible to use characters 1, 2, 3 and 4 to represent specific
    ghost characters. Any other characters are ignored.
    """

    def process_layout_text(self, layout_text):
        """
        The width (x) is how many elements are in a single cell. The
        height (y) is how many cells there are. So this bit of logic
        counts down the rows and, for each row, gets each element of
        that row.
        """
        maximum_y = self.height - 1

        for y in range(self.height):
            for x in range(self.width):
                layout_char = layout_text[maximum_y - y][x]
                self.process_layout_characters(x, y, layout_char)

        self.agent_positions.sort()
        self.agent_positions = [(index == 0, position) for index, position in self.agent_positions]

    def process_layout_characters(self, x, y, character):
        logging.debug("x,y: {},{} = {}".format(x, y, character))

        if character == "%":
            self.walls[x][y] = True
        elif character == ".":
            self.dots[x][y] = True
        elif character == "o":
            self.pellets.append((x, y))
        elif character == "P":
            self.agent_positions.append((0, (x, y)))
        elif character == "G":
            self.agent_positions.append((1, (x, y)))
            self.num_ghosts += 1
        elif character in ['1', '2', '3', '4']:
            self.agent_positions.append((int(character), (x, y)))
            self.num_ghosts += 1

    def is_wall(self, position):
        row, column = position
        return self.walls[row][column]

    def get_ghost_count(self):
        return self.num_ghosts

    def get_random_legal_position(self):
        x = random.choice(range(self.width))
        y = random.choice(range(self.height))

        while self.is_wall((x, y)):
            x = random.choice(range(self.width))
            y = random.choice(range(self.height))

        return x, y

    def get_random_corner(self):
        possibles = [(1, 1), (1, self.height - 2), (self.width - 2, 1), (self.width - 2, self.height - 2)]
        return random.choice(possibles)

    def get_furthest_corner(self, pacumen_position):
        possibles = [(1, 1), (1, self.height - 2), (self.width - 2, 1), (self.width - 2, self.height - 2)]
        distance, position = max([(manhattan_distance(p, pacumen_position), p) for p in possibles])
        return position

    def __init__(self, layout_text):
        self.layout_text = layout_text
        self.width = len(layout_text[0])
        self.height = len(layout_text)
        self.walls = Grid(self.width, self.height, False)
        self.dots = Grid(self.width, self.height, False)
        self.pellets = []
        self.agent_positions = []
        self.num_ghosts = 0
        self.process_layout_text(layout_text)
        self.total_dots = len(self.dots.as_list())
        self.total_pellets = len(self.pellets)

    def __str__(self):
        return "\n".join(self.layout_text)


def load_layout(fullname):
    if not os.path.exists(fullname):
        return None

    layout_file = open(fullname)

    try:
        return Layout([line.strip() for line in layout_file])
    finally:
        layout_file.close()


def get_layout(name, back_path=1):
    """
    This method checks for name.lay in the layouts directory. If the file
    is not found there, it checks for name.lay in the project root. The
    method will append the ".lay" extension for you if it's not provided.
    Finally, the method will also check one level above the project root.
    This can be configured by changing the value of `back_path`.
    """
    if name.endswith(".lay"):
        layout = load_layout("layouts/" + name)

        if layout is None:
            layout = load_layout(name)
    else:
        layout = load_layout("layouts/" + name + ".lay")

        if layout is None:
            layout = load_layout(name + ".lay")

    if layout is None and back_path > 0:
        current_directory = os.path.abspath(".")
        os.chdir("..")
        layout = get_layout(name, back_path - 1)
        os.chdir(current_directory)

    return layout


def test():
    game_layout = get_layout("testing")
    print("Layout as read from file:")
    print(game_layout)
    print("----------------")
    print("Width:", game_layout.width)
    print("Height:", game_layout.height)
    print("----------------")
    print("Walls and Dots are Grids")
    print("----------------")
    print("Walls:\n{}".format(game_layout.walls))
    print("Is 0,0 a wall? (True) -", game_layout.is_wall((0, 0)))
    print("Is 1,1 a wall? (False) -", game_layout.is_wall((1, 1)))
    print("Hash of walls:", hash(game_layout.walls))
    print("----------------")
    print("Dots:\n{}".format(game_layout.dots))
    print("Hash of dots:", hash(game_layout.dots))
    print("Total Dots:", game_layout.total_dots)
    print("Dot Locations:", game_layout.dots.as_list())
    print("----------------")
    print("Total Pellets:", game_layout.total_pellets)
    print("Pellet Locations:", game_layout.pellets)
    print("----------------")
    print("Agent Positions:", game_layout.agent_positions)
    print("----------------")
    pacumen = game_layout.agent_positions[0][1]
    print("Pacumen Position:", pacumen)
    print("----------------")
    print("Ghost Count:", game_layout.get_ghost_count())
    ghost_1 = game_layout.agent_positions[1][1]
    ghost_2 = game_layout.agent_positions[2][1]
    ghost_3 = game_layout.agent_positions[3][1]
    ghost_4 = game_layout.agent_positions[4][1]
    print("First Ghost Position:", ghost_1)
    print("Second Ghost Position:", ghost_2)
    print("Third Ghost Position:", ghost_3)
    print("Fourth Ghost Position:", ghost_4)
    print("----------------")
    print("Get a random legal position: {}".format(game_layout.get_random_legal_position()))
    print("Get another random legal position: {}".format(game_layout.get_random_legal_position()))
    print("----------------")
    print("Get a random corner: {}".format(game_layout.get_random_corner()))
    print("----------------")
    print("Get furthest corner (from Pacumen): {}".format(game_layout.get_furthest_corner(pacumen)))
